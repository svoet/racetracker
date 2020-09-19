import config
class GenericAPIHandler():
    object_class = None
    schema_class = None
    def search(self):
        """
        This function responds to a request for /api/objects
        with the complete lists of objects
        :return:        json string of list of objects
        """
        # Create the list of objects from our data
        objects = self.object_class.query.order_by(self.object_class.id).all()

        # Serialize the data for the response
        schema = self.schema_class(many=True)
        data = schema.dump(objects)
        print("{}".format(data))
        return data


    def get(self,object_id):
        """
        This function responds to a request for /api/objects/{object_id}
        with one matching object from objects
        :param object_id:   Id of object to find
        :return:            object matching id
        """
        # Get the object requested
        object = self.object_class.query.filter(self.object_class.id == object_id).one_or_none()

        # Did we find a object?
        if object is not None:

            # Serialize the data for the response
            schema = self.schema_class()
            data = schema.dump(object)
            return data

        # Otherwise, nope, didn't find that object
        else:
            abort(
                404,
                "self.object_class not found for Id: {object_id}".format(object_id=object_id),
            )


    def post(self,object):
        """
        This function creates a new object in the objects structure
        based on the passed in object data
        :param object:  object to create in objects structure
        :return:        201 on success, 406 on object exists
        """
        id = object.get("id")

        existing_object = (
            self.object_class.query.filter(self.object_class.id == id)
            .one_or_none()
        )

        # Can we insert this object?
        if existing_object is None:

            # Create a object instance using the schema and the passed in object
            schema = self.schema_class()
            new_object = schema.load(object, session=config.db.session)

            # Add the object to the database
            config.db.session.add(new_object)
            config.db.session.commit()

            # Serialize and return the newly created object in the response
            data = schema.dump(new_object)

            return data, 201

        # Otherwise, nope, object exists already
        else:
            abort(
                409,
                "self.object_class {fname} {lname} exists already".format(
                    fname=fname, lname=lname
                ),
            )


    def put(self,object_id, object):
        """
        This function updates an existing object in the objects structure
        Throws an error if a object with the name we want to update to
        already exists in the database.
        :param object_id:   Id of the object to update in the objects structure
        :param object:      object to update
        :return:            updated object structure
        """
        # Get the object requested from the db into session
        update_object = self.object_class.query.filter(
            self.object_class.id == object_id
        ).one_or_none()


        # Are we trying to find a object that does not exist?
        if update_object is None:
            abort(
                404,
                "self.object_class not found for Id: {object_id}".format(object_id=object_id),
            )

        # Otherwise go ahead and update!
        else:

            # turn the passed in object into a db object
            schema = self.schema_class()
            update = schema.load(object, session=config.db.session)

            # Set the id to the object we want to update
            update.id = update_object.id

            # merge the new object into the old and commit it to the db
            config.db.session.merge(update)
            config.db.session.commit()

            # return updated object in the response
            data = schema.dump(update_object)

            return data, 200


    def delete(self,object_id):
        """
        This function deletes a object from the objects structure
        :param object_id:   Id of the object to delete
        :return:            200 on successful delete, 404 if not found
        """
        # Get the object requested
        object = self.object_class.query.filter(self.object_class.id == object_id).one_or_none()

        # Did we find a object?
        if object is not None:
            config.db.session.delete(object)
            config.db.session.commit()
            return "self.object_class {object_id} deleted".format(object_id=object_id), 200

        # Otherwise, nope, didn't find that object
        else:
            return "self.object_class not found for Id: {object_id}".format(object_id=object_id), 404
