from world import World



if __name__ == "__main__":
    map_instance = World(path = None, init_pygame=True, width=50, height=30) # To create a new world, provide path = None
    map_instance.run()
