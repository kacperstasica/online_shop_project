import redis

from myshop import settings

# connect to Redis
from shop.models import Product

r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
)


class Recommender:

    def get_product_key(self, id):
        return f'product: {id}:purchased_with'

    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # get the other product bought with each product
                if product_id != with_id:
                    # increment score for product bought together
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products, max_results=6):
        products_ids = [p.id for p in products]
        if len(products) == 1:
            # only one product
            suggestions = r.zrange(
                self.get_product_key(products_ids[0]),
                0, -1, desc=True)[:max_results]
        else:
            # generate temporary key
            flat_ids = [str(id) for id in products_ids]
            tmp_key = f'tmp_{flat_ids}'
            # multiple products combine scores of all products
            # store the resulting temporary set in a temporary key
            keys = [self.get_product_key(id) for id in products_ids]
            r.zunionstore(tmp_key, keys)
            # remove ids for the products recommendation is for
            r.zrem(tmp_key, *products_ids)
            # get the product ids by their score (descendant sort)
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # remove the temporary key
            r.delete(tmp_key)
        suggested_product_ids = [int(id) for id in suggestions]
        # get suggested products and sort by order of appearance
        suggested_products = list(Product.objects.filter(id__in=suggested_product_ids))
        suggested_products.sort(key=lambda x: suggested_product_ids.index(x.id))
        return suggested_products

    def clear_purchases(self):
        for id in Product.objects.value_list('id', flat=True):
            r.delete(self.get_product_key(id))
