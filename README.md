# Azure IoT Edge + Custom Vision
## Requirements
- Azure Conatiner Registry (User Name & Password)

- Azure IoT Hub (IoT Edge Device needed)

- Exported Custom Vision model (Dockerfile)

- Visual Studio Code

- Linux Device (with Web cam)

## Procedure
1. Refer [this](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-docker-cli#prerequisites) web page and upload your model image to Azure Container Registry.
	- Unzip Exported Custom Vision model and build image from that folder (Dockerfile is included in the folder)

2. Open **.env** file, enter **USER NAME and PASSWORD** of Azure Container Registry and uploaded model image **PATH** which you have done above.
	- **PATH** is **YOUR\_AZURE\_CONTAINER\_REGISTRY\_LOGIN_SERVER/IMAGE\_NAME:TAG**

3. Follow [this](https://docs.microsoft.com/en-us/azure/iot-edge/quickstart-linux) quick start to ready your Linux device.

4. Open this repo with Visual studio and deploy the modules on the device with [this](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-develop-for-linux#build-and-push-your-solution) guide.

5. Enjoy Azure IoT Edge :)

## FYI
- Model module gets octet stream format images through port 80. (custom vision Dockerfile exported model's default)
- As using camera module, the camera frame can be observed through 0.0.0.0:5000
