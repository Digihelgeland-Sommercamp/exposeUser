# Expose User
Expose user is one of multiple micro services for redusert foreldrebetaling. Visit the [main repo](https://github.com/Altinn/summer-camp-2021) to get an overview and read more documentation.

Expose user is intended to be a communication layer between the databes and the rest of the back-end.
It is coupled with the following microservices:
* [Hub sevice](https://github.com/Digihelgeland-Sommercamp/hubService)


## API
Every route can be found in [app.py](https://github.com/Digihelgeland-Sommercamp/exposeUser/blob/main/app.py)   
Each route below links to the OpenAPI specification on swaggerhub.

* [GET] [/applications/<saksnummer>](https://app.swaggerhub.com/apis/emilwhj/exposeUser/0.1#/default/get_applications__saksnummer_)
* [GET] [/applications/<saksnummer>/status](https://app.swaggerhub.com/apis/emilwhj/exposeUser/0.1#/default/get_applications__saksnummer__status)
* [GET] [/all_applications/<personidentifikator>](https://app.swaggerhub.com/apis/emilwhj/exposeUser/0.1#/default/get_all_applications__personidentifikator_)
* [POST] [/applications/<saksnummer>/update_status](https://app.swaggerhub.com/apis/emilwhj/exposeUser/0.1#/default/post_applications__saksnummer__update_status)
* [POST] [/applications/submit_application](https://app.swaggerhub.com/apis/emilwhj/exposeUser/0.1#/default/post_applications_submit_application)

### Installation
This service is intended to run in a kubernetes cluster with the [Hub sevice](https://github.com/Digihelgeland-Sommercamp/hubService). It makes no sense for this service to run alone.

You can use the [deployment.yaml](https://github.com/Digihelgeland-Sommercamp/exposeUser/deployment.yaml) to create a deployment in kubernetes, and [service.yaml](https://github.com/Digihelgeland-Sommercamp/exposeUser/serviceyaml) to create a service.

[The latest docker image can be found here](https://hub.docker.com/repository/docker/johannesdigdir/expose_user)



### Architecture
Visual representation of the microservices:
![Picture of the architecture and coupling of the services](https://github.com/Altinn/summer-camp-2021/blob/main/Documentation/Architecture/Microservice%20overview.png "Picture of the architecture and coupling of the services")