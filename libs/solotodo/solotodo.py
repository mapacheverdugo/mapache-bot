


import schedule
from peewee import *
from telegram import LinkPreviewOptions

from database import *
from libs.solotodo.models.price import Price
from libs.solotodo.models.product import Product
from libs.solotodo.models.product_subscription import ProductSubscription
from libs.solotodo.scrapper import *
from messager import MessagerInterface
from models.process_step import ProcessStep
from utils import escape_markdown_v2, format_currency


class SoloTodo:
    
    def __init__(self, messager: MessagerInterface):
        self.messager = messager
        
        db.create_tables([ProductSubscription, Product, Price, Store])
        
        #self.get_lowest_historical_prices(Product.get_or_none(Product.id == 2))
        self.schedule_jobs()
        
    def schedule_jobs(self):
        subscriptions = ProductSubscription.select()
        for subscription in subscriptions:
            self.check_prices(subscription)
            schedule.every(subscription.poll_interval).minutes.do(self.check_prices, subscription)

    def get_lowest_historical_prices(self, product, limit=3):
        normal_prices = list((Price.select().where(Price.product_id == product.id, Price.normal_price > 0).order_by(Price.timestamp.desc())).group_by(Price.normal_price).order_by(Price.normal_price.asc()).limit(limit))
        offer_prices = list((Price.select().where(Price.product_id == product.id, Price.offer_price > 0).order_by(Price.timestamp.desc())).group_by(Price.offer_price).order_by(Price.offer_price.asc()).limit(limit))

        return (normal_prices, offer_prices)

    
    def check_prices(self, subscription):
        product = subscription.product
        current_prices = get_current_prices(product)
        historical_lowest_prices = self.get_lowest_historical_prices(product, limit=1)

        latest_seen_prices = (subscription.latest_seen_normal_lower_price, subscription.latest_seen_offer_lower_price)
        
        if current_prices[0] is None or current_prices[1] is None:
            return
            
        
        
        if (latest_seen_prices[0] is None or
            latest_seen_prices[1] is None or
            current_prices[0].normal_price < latest_seen_prices[0].normal_price or
            current_prices[1].offer_price < latest_seen_prices[1].offer_price):
        
            normal_latest_seen_notify_price = latest_seen_prices[0].normal_price * (1 - subscription.latest_seen_variation_from_notify)
            normal_historical_notify_price = historical_lowest_prices[0][0].normal_price * (1 - subscription.historical_variation_until_notify)

            offer_latest_seen_notify_price = latest_seen_prices[1].offer_price * (1 - subscription.latest_seen_variation_from_notify)
            offer_historical_notify_price = historical_lowest_prices[1][0].offer_price * (1 - subscription.historical_variation_until_notify)

            should_notify_normal_latest_seen = current_prices[0].normal_price < normal_latest_seen_notify_price
            should_notify_offer_latest_seen = current_prices[1].offer_price < offer_latest_seen_notify_price
            should_notify_latest_seen = should_notify_normal_latest_seen or should_notify_offer_latest_seen

            should_notify_normal_historical = current_prices[0].normal_price < normal_historical_notify_price
            should_notify_offer_historical = current_prices[1].offer_price < offer_historical_notify_price
            should_notify_historical = should_notify_normal_historical or should_notify_offer_historical
            

            

            if should_notify_latest_seen:
                emoji = " 🔥🔥🔥 " if should_notify_historical else ""

                message_lines = [
                    f"{emoji}El precio de {subscription.custom_name} ha cambiado{emoji}",
                    "",
                ]

                lastest_seen_normal_price_store = self.get_store(latest_seen_prices[0].store_solotodo_id)
                lastest_seen_offer_price_store = self.get_store(latest_seen_prices[1].store_solotodo_id)


                message_lines.append(self.prices_message_variation("normal", latest_seen_prices[0].normal_price, current_prices[0].normal_price), lastest_seen_normal_price_store)
                message_lines.append(self.prices_message_variation("oferta", latest_seen_prices[1].offer_price, current_prices[1].offer_price), lastest_seen_offer_price_store)
            
                message_lines.append("")
                
                message_lines.extend(self.product_prices_now_messages(current_prices[0], current_prices[1], lastest_seen_normal_price_store, lastest_seen_offer_price_store))

                self.messager.send_message(
                    subscription.user.user_id,
                    "\n".join(message_lines),
                    parse_mode='MarkdownV2',
                    link_preview_options=LinkPreviewOptions(
                        is_disabled=True
                    )
                )

        subscription.latest_seen_normal_lower_price = current_prices[0]
        subscription.latest_seen_offer_lower_price = current_prices[1] 
        subscription.save()

    def store_details_text(self, price, store, is_offer=False, add_link=True):
        str = f"en [{store.name}]({price.external_url})" if add_link else f"en {store.name}"
        if is_offer:
            if store.preferred_payment_method is not None:
                str += f" con {store.preferred_payment_method}"
            else:
                str += " con efectivo"
        return str

    def prices_message_variation(self, price_name, latest_price, current_price, store):
        variation_percentage = (latest_price / current_price) * 100

        if variation_percentage > 100:
            return f"El precio {price_name} ha subido, antes era ~{format_currency(latest_price)}~ y ahora es {format_currency(current_price)} ({variation_percentage:.2f}% de aumento)"
        elif variation_percentage < 100:
            return f"¡El precio {price_name} ha bajado {self.store_details_text(current_price, store, price_name == 'oferta')}! Antes era ~{format_currency(latest_price)}~ y ahora es {format_currency(current_price)} ({variation_percentage:.2f}% de descuento)"
        else:
            return f"El precio {price_name} se mantiene en {format_currency(current_price)} {self.store_details_text(current_price, store, price_name == 'oferta')}"

    def add_start(self, user):
        user.current_step = ProcessStep.SOLOTODO_ADD_WAITING_URL.value
        user.save()
        self.messager.send_message(user.user_id, "Envia el link del producto que deseas seguir")

    def middle_step(self, message, user):
        if user.current_step == ProcessStep.SOLOTODO_ADD_WAITING_URL.value:
            self.add_set_url(message, user)
        elif user.current_step == ProcessStep.SOLOTODO_ADD_WAITING_NAME.value:
            self.add_set_name(message, user)
        elif user.current_step == ProcessStep.SOLOTODO_EDIT_WAITING_ID.value:
            self.edit_set_id(message, user)
        elif user.current_step == ProcessStep.SOLOTODO_EDIT_WAITING_ATTRIBUTE.value:
            self.edit_set_attribute(message, user)
        elif user.current_step == ProcessStep.SOLOTODO_DELETE_WAITING_ID.value:
            self.delete_set_id(message, user)
        else:
            user.current_step = ProcessStep.INITIAL.value
            user.save()
            raise Exception("Unknown command or step")
        
    def extract_id_or_url(self, message):
        if 'solotodo.cl/products/' in message:
            id = message.split('solotodo.cl/products/')[1].split('-')[0]
        elif message.isdigit():
            id = message
        else:
            return None

        return id

    def add_set_url(self, url_or_id, user):
        not_valid_message = "El link o ID no es válido, intenta nuevamente"

        id = self.extract_id_or_url(url_or_id)
        if id is None:
            self.messager.send_message(user.user_id, not_valid_message)
            return
        
        product = Product.get_or_none(Product.solotodo_id == id)
        current_subscriptions = []
        if product is not None:
            current_subscriptions = ProductSubscription.select().where(ProductSubscription.user == user and ProductSubscription.product == product)

        if len(current_subscriptions) > 0:
            self.messager.send_message(user.user_id, "Ya tienes este producto en seguimiento. Prueba agregando otro producto o vuelver al menú con /start")
            return

        product_summary = get_product_summary(id)

        if product_summary is None or product_summary.product is None:
            self.messager.send_message(user.user_id, not_valid_message)
            return
        
        product_summary.product.save()

        if product_summary.lower_offer_price is not None:
            product_summary.lower_offer_price.save()

        if product_summary.lower_normal_price is not None:
            product_summary.lower_normal_price.save()

        list(map(lambda price: price.save(), product_summary.pricing_history))

        is_available = product_summary.lower_offer_price is not None and product_summary.lower_normal_price is not None
        
        subscription = ProductSubscription.create(
            custom_name=product_summary.product.name,
            user=user,
            product=product_summary.product,
            poll_interval=60,
            url=product_summary.product.url,
            last_seen_available=is_available,
            first_seen_normal_lower_price=product_summary.lower_normal_price,
            first_seen_offer_lower_price=product_summary.lower_offer_price,
            latest_seen_normal_lower_price=product_summary.lower_normal_price,
            latest_seen_offer_lower_price=product_summary.lower_offer_price,
        )

        if is_available:
            offer_price_store = self.get_store(product_summary.lower_offer_price.store_solotodo_id)
            normal_price_store = self.get_store(product_summary.lower_normal_price.store_solotodo_id)

            message_lines = [
                escape_markdown_v2(f'¡Producto "{product_summary.product.name}" guardado con éxito!'),
                "",
            ]

            message_lines.extend(self.product_prices_now_messages(product_summary.lower_normal_price, product_summary.lower_offer_price, normal_price_store, offer_price_store))

            message_lines.append("")
            message_lines.extend(self.product_pricing_history_summary(product_summary.product))
            
            message_lines.extend(["",
                f"Revisaremos cada {subscription.poll_interval} minutos si hay cambios en el precio de este producto y te notificaremos si baja de precio",
                "",
                "Si tienes otro producto que quieras seguir, envía el link o ID del producto, de lo contrario, puedes volver al menu con /start"
            ])

            self.messager.send_message(
                user.user_id, 
                "\n".join(message_lines),
                parse_mode='MarkdownV2',
                link_preview_options=LinkPreviewOptions(
                    is_disabled=True
                )
            )
        else:
            message_lines = [
                escape_markdown_v2(f'¡Producto "{product_summary.product.name}" guardado con éxito!'),
                "",
                "Este producto no está disponible actualmente, te notificaremos cuando vuelva a estar disponible",
                "",
                "Si tienes otro producto que quieras seguir, envía el link o ID del producto, de lo contrario, puedes volver al menu con /start"
            ]

            self.messager.send_message(
                user.user_id, 
                "\n".join(message_lines),
                parse_mode='MarkdownV2'
            )

    def product_prices_now_messages(self, normal_price, offer_price, normal_price_store, offer_price_store):
        prices_are_the_same = normal_price.normal_price == offer_price.offer_price
        stores_are_the_same = normal_price_store.solotodo_id == offer_price_store.solotodo_id
        if (prices_are_the_same and stores_are_the_same):
            return [
                f"Actualmente su *precio con todo medio de pago* más bajo es: {escape_markdown_v2(format_currency(normal_price.normal_price))} en [{escape_markdown_v2(normal_price_store.name)}]({normal_price.external_url})",
            ]

        return [
            f"Actualmente su *precio normal* más bajo es: {escape_markdown_v2(format_currency(normal_price.normal_price))} {self.store_details_text(normal_price, normal_price_store)}",
            f"Actualmente su *precio oferta* más bajo es: {escape_markdown_v2(format_currency(offer_price.offer_price))} {self.store_details_text(offer_price, offer_price_store, is_offer=True)}",
        ]
    
    def product_pricing_history_summary(self, product, limit=10):
        message_lines = []

        historical_lowest_prices = self.get_lowest_historical_prices(product, limit=limit)

        message_lines.append(f"Como referencia, los precios históricos más bajos registrados en un año son")

        for i in range(len(historical_lowest_prices[0])):
            normal_price = historical_lowest_prices[0][i]
            offer_price = historical_lowest_prices[1][i]

            historical_lowest_normal_price_store = self.get_store(normal_price.store_solotodo_id)
            historical_lowest_offer_price_store = self.get_store(offer_price.store_solotodo_id)

            message_lines.append("")
            message_lines.append(escape_markdown_v2(f"Precio normal: {format_currency(normal_price.normal_price)} {self.store_details_text(normal_price, historical_lowest_normal_price_store, add_link=False)} el {normal_price.timestamp.strftime('%d/%m/%Y')}"))
            message_lines.append(escape_markdown_v2(f"Precio oferta: {format_currency(offer_price.offer_price)} {self.store_details_text(offer_price, historical_lowest_offer_price_store, add_link=False, is_offer=True)} el {offer_price.timestamp.strftime('%d/%m/%Y')}"))

        return message_lines


    def get_store(self, id):
        store = Store.get_or_none(Store.solotodo_id == id)
        if store is None:
            store = get_store(id)
            store.save()
        return store


    def add_set_name(self, name, user):
        item = ProductSubscription.select().where(ProductSubscription.user == user).order_by(ProductSubscription.created_at.desc()).get()
        item.name = name
        item.saved = True
        item.save()

        user.current_step = ProcessStep.INITIAL.value
        user.save()

        self.messager.send_message(user.user_id, "Producto guardado con éxito")


    

