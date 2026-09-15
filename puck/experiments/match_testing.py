read = ("kill")
self = object()


print("Started Test_run")
first_message=self.recieve()
assert first_message[0]=="drawing_queue"  ## THIS IS WHAT YOU SHOULD GET
## local variables
drawing_queue= first_message[1]
associated_canvas_ids=[]
spawned_actors=[]

match read:
    case ("kill"):
        self.end()
    case ("new_shape",("type", type),("coordinates", coordinates)):
        drawing_queue.put(("action", ("new", ("type", type), ("sender", self), ("coordinates"), coordinates,)))
    case ("update_shape",("id", id), ("coordinates", coordinates)):
        drawing_queue.put(("action", ("update", ("id", id), ("coordinates", coordinates))))
    case ("information", *info):
        match info:
            case ("add_ids", id_list):
                associated_canvas_ids.append(id_list)
            case _ as info:
                print(info)