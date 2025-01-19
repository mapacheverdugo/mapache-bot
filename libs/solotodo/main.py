
from peewee import *

from database import *
from libs.solotodo.models.price import Price
from libs.solotodo.models.product import Product
from libs.solotodo.models.product_subscription import ProductSubscription
from libs.solotodo.scrapper import *
from messager import MessagerInterface
from models.process_step import ProcessStep


class SoloTodo:
    
    def __init__(self, messager: MessagerInterface):
        self.messager = messager
        
        db.create_tables([ProductSubscription, Product, Price])
        

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
        
    def validate_id_or_url(self, message):
        if 'solotodo.cl/products/' in message:
            id = message.split('solotodo.cl/products/')[1].split('-')[0]
        elif message.isdigit():
            id = message
        else:
            return None

        product = get_product_summary(id)

        return product
        

    def add_set_url(self, url_or_id, user):
        product = self.validate_id_or_url(url_or_id)

        if product is None:
            self.messager.send_message(user.user_id, "El link o ID no es válido, intenta nuevamente")
            return

        product.current_normal_lower_price.save()
        product.current_offer_lower_price.save()
        product.save()
        
        ProductSubscription.create(
            custom_name=product.name,
            user=user,
            product=product,
            poll_interval=60,
            url=product.url,
            saved=True
        )

        messageLines = [
            f'¡Producto "{product.name}" guardado con éxito\!',
            "",
            f"Su precio normal más bajo actualmente es: {product.current_normal_lower_price.normal_price} en [{product.current_normal_lower_price.store_name}]({product.current_normal_lower_price.store_url})",
            f"Su precio oferta más bajo actualmente es: {product.current_offer_lower_price.offer_price} en [{product.current_normal_lower_price.store_name}]({product.current_normal_lower_price.store_url})",
            "",
            "Revisaremos cada 60 minutos si hay cambios en el precio de este producto y te notificaremos si baja de precio",
        ]



        self.messager.send_message(
            user.user_id, 
            "\n".join(messageLines),
            parse_mode='MarkdownV2'
        )


    def add_set_name(self, name, user):
        item = ProductSubscription.select().where(ProductSubscription.user == user).order_by(ProductSubscription.created_at.desc()).get()
        item.name = name
        item.saved = True
        item.save()

        user.current_step = ProcessStep.INITIAL.value
        user.save()

        self.messager.send_message(user.user_id, "Producto guardado con éxito")


    

