"""Packaged basic mongoDB processing handler."""
import pymongo


class MongoDBHandler(object):
    """Implemented database handler for MongoDB."""

    def __init__(self, host: str, port: int,
                 usr: str, pwd: str, **kwargs):
        """
        Create a :class:`MongoClient` instance to handle data.

        :param host: database host.
        :param port: database port.
        :param usr: username.
        :param pwd: user password,
        :param kwargs: other variables can be passed to :class:`MongoClient`.
        """
        self.client = pymongo.MongoClient(host, port, **kwargs)
        self.admin = self.client.admin
        self.admin.authenticate(usr, pwd)

    # def update(self, database: str, collection: str,
    #            filters: dict, updates: dict, mode: str='one',
    #            **kwargs) -> pymongo.results.UpdateResult:
    #     """
    #     Update documents(s) in specific collection by modifications.
    #
    #     :param database: database name.
    #     :param collection: collection name.
    #     :param filters: a query that matches the document to update.
    #     :param updates: the modifications to apply.
    #     :param mode: can be `one` or `many`, defaults to `one`.
    #         `one` means update a single document matching the filter.
    #         `many` means update one or more documents matching the filter.
    #     :param kwargs: other variables can be passed to
    #      :meth:`pymongo.collection.Collection.update_one`
    #      or :meth:`pymongo.collection.Collection.update_many`.
    #     :return: an instance of :class:`pymongo.results.UpdateResult`.
    #     """
    #     if mode not in ['one', 'many']:
    #         raise ValueError('Wrong mode setting in updating.')
    #     db = self.client[database]
    #     col = db[collection]
    #     if mode == 'one':
    #         return col.update_one(filters, updates, **kwargs)
    #     else:
    #         return col.update_many(filters, updates, **kwargs)
    #
    # def delete(self, database: str, collection: str, filters: dict,
    #            mode: str='one', **kwargs) -> pymongo.results.DeleteResult:
    #     """
    #     Delete document(s) matching the filters in specific collection.
    #
    #     :param database: database name.
    #     :param collection: collection name.
    #     :param filters: a query that matches the documents to delete.
    #     :param mode: can be `one` or `many`, defaults to `one`.
    #         `one` means delete a single document matching the filter.
    #         `many` means delete one or more documents matching the filter.
    #     :param kwargs: other variables can be passed to
    #      :meth:`pymongo.collection.Collection.delete_one`
    #      or :meth:`pymongo.collection.Collection.delete_many`.
    #     :return: an instance of :class:`pymongo.results.DeleteResult`.
    #     """
    #     if mode not in ['one', 'many']:
    #         raise ValueError('Wrong mode setting in deleting.')
    #     db = self.client[database]
    #     col = db[collection]
    #     if mode == 'one':
    #         return col.delete_one(filters, **kwargs)
    #     else:
    #         return col.delete_many(filters, **kwargs)
    #
    # def create(self, database: str, name: str, **kwargs):
    #     """
    #     Create a new collection in this database.
    #
    #     :param database: database name.
    #     :param name: collection name.
    #     :param kwargs: other variables can be passed to
    #      :meth:`pymongo.database.Database.create_collection`.
    #     """
    #     db = self.client[database]
    #     db.create_collection(name, **kwargs)
    #
    # def drop(self, database: str, name: str, **kwargs):
    #     """
    #     Drop a collection in this database.
    #
    #     :param database: database name.
    #     :param name: collection name.
    #     :param kwargs: other variables can be passed to
    #      :meth:`pymongo.database.Database.drop_collection`.
    #     """
    #     db = self.client[database]
    #     db.drop_collection(name, **kwargs)
    #
    # def rename(self, database: str, name: str, new_name: str, **kwargs):
    #     """
    #     Rename the collection.
    #
    #     :param database: database name.
    #     :param name: original collection name.
    #     :param new_name: new name for this collection.
    #     :param kwargs: other variables can be passed to
    #      :meth:`pymongo.collection.Collection.rename`.
    #     """
    #     db = self.client[database]
    #     col = db[name]
    #     col.rename(new_name, **kwargs)
