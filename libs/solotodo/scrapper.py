

import datetime

import pyshorteners
import requests
from retrying import retry

from libs.solotodo.models.price import Price
from libs.solotodo.models.product import Product


@retry(stop_max_attempt_number=3)
def get_current_prices(id_product):
    url = f"https://publicapi.solotodo.com/products/available_entities/?ids={id_product}"
    data = requests.get(url).json()
    
    idp = data['results'][0]['entities'][0]['id']
    nombre_producto = data['results'][0]['entities'][0]['name']
    external_url = data['results'][0]['entities'][0]['external_url']
    slug = data['results'][0]['product'][0]['slug']
    offer_price = data['results'][0]['entities'][0]['active_registry']['offer_price']
    offer_price = format(int(float(offer_price)), ',')
    solotodo_url = "https://www.solotodo.cl/products/" + str(idp) + "-" + str(slug)
    return  f"El producto `{nombre_producto}` bajó de precio:\n\n👉`{offer_price}`👈  \n\n [LINK PRODUCTO ❗]({external_url}) [❗ SOLOTODO]({solotodo_url})"

        
@retry(stop_max_attempt_number=3)
def get_product_summary(id):
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        timedelta = datetime.timedelta(days=365)
        delta_datetime = now - timedelta

        product_url = f"https://publicapi.solotodo.com/products/{id}/pricing_history/?timestamp_after={delta_datetime.isoformat()}&timestamp_before={now.isoformat()}&exclude_refurbished=false"
        product_data = requests.get(product_url).json()

        first_entity = product_data[0]['entity']
        name = first_entity['name']
        product_url = first_entity['url']
        external_url = first_entity['external_url']

        store_data = requests.get(first_entity['store']).json()

        current_offer_lower_price = None
        current_normal_lower_price = None

        for entity in product_data:
            active_registry = entity['entity']['active_registry']
            if active_registry is not None:
                price = Price(
                    normal_price=format(int(float(active_registry['normal_price']))),
                    offer_price=
                    format(int(float(active_registry['offer_price']))),
                    store_name=store_data['name'],
                    store_url=external_url,
                    timestamp=datetime.datetime.now()
                )

                if current_offer_lower_price is None or price.offer_price < current_offer_lower_price.offer_price:
                    current_offer_lower_price = price
                if current_normal_lower_price is None or price.normal_price < current_normal_lower_price.normal_price:
                    current_normal_lower_price = price
                break

        return Product(
            solotodo_id=int(id),
            name=name,
            url=product_url,
            current_offer_lower_price=current_offer_lower_price,
            current_normal_lower_price=current_normal_lower_price
        )
    except Exception as e:
        print(e)
        return None





""" def pDesc(price):

    oldItems = fl.itemS_all('items.db','items')
    nItems = len(oldItems)
    if nItems != 0:
        for item in oldItems:
                if int(item[1]) != int(price):
                    if int(item[1]) > int(price):                 
                        valor_original = int(item[1])
                        valor_nuevo = int(price)
                        descuento = valor_original - valor_nuevo
                        porcentaje_descuento = (descuento * 100) / valor_original
                        porcentaje_descuento = round(porcentaje_descuento, 2)
                        return (int(porcentaje_descuento*0.01)) 
 

def textDescuento(price):
    descuento = pDesc(price)
    if descuento >= 0 and descuento <= 10:
        return  f"💩\n"
    elif descuento > 10 and descuento <= 30:
        return  f"😊\n"
    elif descuento > 30 and descuento <= 50:
        return  f"😲\n"
    elif descuento > 50 and descuento <= 60:
        return  f"🤑\n"
    elif descuento > 60  and descuento <= 80:
        return  f"🅱\n"
    elif descuento > 80 and descuento <= 90:
        return  f"🅰\n"
    elif descuento >= 90 and descuento <= 100:
        return  f"🔥\n"
    else:
        return f"🤔\n"
        """