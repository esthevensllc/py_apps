from controller import Controller


if __name__ == '__main__':
    controller = Controller()
    df = controller.obtenerDatos()
    controller.borrarDatos()
    controller.InsertarDF(df)

