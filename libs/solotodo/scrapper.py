

import datetime

import requests
from retrying import retry

from libs.solotodo.models.price import Price
from libs.solotodo.models.product import Product
from libs.solotodo.models.product_summary import ProductSummary
from libs.solotodo.models.store import Store

base_url = "https://publicapi.solotodo.com"
mock_base_url = "https://mock.apidog.com/m1/794146-772682-default"

@retry(stop_max_attempt_number=3)
def get_current_prices(product: Product):
    url = f"{base_url}/products/available_entities/?ids={product.solotodo_id}"
    data = requests.get(url).json()
    
    result = data['results'][0]

    return lower_prices_from_list_of_entities(result['entities'], product)

@retry(stop_max_attempt_number=3)
def get_store(id: int):
    url = f"{base_url}/stores/{id}"
    data = requests.get(url).json()
    
    return Store(
        solotodo_id=int(id),
        name=data['name'],
        logo_url=data['logo'],
        preferred_payment_method=data['preferred_payment_method']
    )
    
        
@retry(stop_max_attempt_number=3)
def get_product_summary(id: int):
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        timedelta = datetime.timedelta(days=365)
        delta_datetime = now - timedelta

        product_url = f"{base_url}/products/{id}/pricing_history/?timestamp_after={delta_datetime.isoformat()}&timestamp_before={now.isoformat()}&exclude_refurbished=false"
        product_data = requests.get(product_url).json()
        
       

        first_entity = product_data[0]['entity']
        name = first_entity['name']
        url = f"{base_url}/products/{id}"

        product = Product(
            solotodo_id=int(id),
            name=name,
            url=url,
        )

        prices = lower_prices_from_list_of_entities(list(map(lambda e: e['entity'], product_data)), product)
        
        pricing_history = []
        for entity in product_data:
            pricing_history.extend(parse_pricing_history_single_entity(entity['entity'], product, entity['pricing_history']))


        return ProductSummary(
            product=product,
            lower_offer_price=prices[1],
            lower_normal_price=prices[0],
            pricing_history=pricing_history,
        )

        
    except Exception as e:
        print(e)
        return None
    
def parse_pricing_history_single_entity(entity, product, pricing_history):
    history = []

    for price in pricing_history:
        store_id = entity['store'].split('solotodo.com/stores/')[1].split('/')[0]
        external_url = entity['external_url']
        price_model = parse_price(price, product, store_id, external_url)
        history.append(price_model)
    
    return history


def lower_prices_from_list_of_entities(entities, product):
    lower_offer_price = None
    lower_normal_price = None

    lower_offer_price_entity = None
    lower_normal_price_entity = None
    

    for entity in entities:
        active_registry = entity['active_registry']
        if active_registry is not None and active_registry['is_available']:
            normal_price = int(float(active_registry['normal_price']))
            offer_price = int(float(active_registry['offer_price']))

            if lower_offer_price_entity is None or offer_price < lower_offer_price:
                lower_offer_price = offer_price
                lower_offer_price_entity = entity
            if lower_normal_price_entity is None or normal_price < lower_normal_price:
                lower_normal_price = normal_price
                lower_normal_price_entity = entity
    
    if lower_offer_price_entity is None or lower_normal_price_entity is None:
        return (None, None)
    
    normal_store_id = lower_normal_price_entity['store'].split('solotodo.com/stores/')[1].split('/')[0]
    offer_store_id = lower_offer_price_entity['store'].split('solotodo.com/stores/')[1].split('/')[0]
    
    normal_active_registry = lower_normal_price_entity['active_registry']
    offer_active_registry = lower_offer_price_entity['active_registry']
    
    return (
        parse_price(
            normal_active_registry,
            product,
            store_solotodo_id=normal_store_id,
            external_url=lower_normal_price_entity['external_url']
        ),
        parse_price(
            offer_active_registry,
            product,
            store_solotodo_id=offer_store_id,
            external_url=lower_offer_price_entity['external_url']
        )
    )

def formating_datetime(datetime_iso):
    return datetime.datetime.fromisoformat(datetime_iso.split('.')[0].replace("Z", ""))


def parse_price(active_registry, product: Product, store_solotodo_id = None, external_url = None, ):
    return Price(
        product=product,
        solotodo_id=int(active_registry['id']),
        normal_price=int(float(active_registry['normal_price'])),
        offer_price=int(float(active_registry['offer_price'])),
        store_solotodo_id=store_solotodo_id,
        external_url=external_url,
        timestamp=formating_datetime(active_registry['timestamp'])
    )
