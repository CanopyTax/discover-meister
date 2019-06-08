# Discover Meister!


![logo](https://assets.pinshape.com/uploads/image/file/26649/container_star-wars-mse-6-mouse-droid-body-for-1-24-rc-car-chassis-3d-printing-26649.JPG)

Discover-Meister is a discovery service that goes the last mile.

The main goal of this project is to provide a service discovery registry that solves the last mile problems.
Many many other service discovery tools exist. But they really only solve one problem in service discovery. 
Really, there are three parts to service discovery:

1) What services/endpoints exist?
2) Where does a service live?
3) What other data about the service can I get?

Existing tools such as consul/zookeeper/eureka/kubernetes/etc. only solve the 2nd problem.
They only tell you where a service is. They do not tell you which endpoints exist and which service owns which endpoints.
They *can* be used to solve 3, but it takes some work. This project attempts to do 1 and 2, leaving #2 (the hardest part)
to those other tools. This does not replace existing service discovery tools, it works with them to solve the last mile problems.

For more details on this, read [this blog post.](https://medium.com/@nhumrich/your-service-discovery-is-not-service-discovery-f5a2c04bc986) 


## Running

The easiest way to run discover meister is with docker-compose:

```
docker-compose up
```

If you have already ran it before, and there are some changes,
you might have to type

```
docker-compose build
docker-compose up
```

## client endpoints



## list of all current endpoints

 
