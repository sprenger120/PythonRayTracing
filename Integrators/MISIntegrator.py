from Integrators.integrator import Integrator
from ray import Ray
import numpy as np
import util as util
from Shapes.Triangle import  Triangle
import copy
import time
from Shapes.Lights.LightBase import LightBase

"""
Angles on the sphere


   seen from above:
      .........
     .       /  .
   .        /     .
   .       /  phi  .
   .      x _______. 0°
   .              .
   . .        . .
       .......
 0 - 180°;  -1 - 1


 seen from the side:
 
  0 - 90°;   0 - 1
                  theta
         ......0°.......
       .       |   /   .
     .         |  /      .
    .          | /        .
   .___________x__________.
"""



class MISIntegrator(Integrator):

    TracePrepTimeSec = 0
    RayGenTimeSec = 0
    ColorGenTimeSec = 0

    sampleCount = 16
    defaultHemisphereNormal = [0, 0, 1]


    def ell(self, scene, ray):
        hitSomething = scene.intersectObjects(ray)
        hitSomething |= scene.intersectLights(ray)

        # we have it an object
        if  hitSomething :

            if isinstance(ray.firstHitShape, LightBase):
                # we have hit light
                return ray.firstHitShape.color
            else:
                # intersection point where object was hit
                ray.d = ray.d / np.linalg.norm(ray.d)
                intersPoint = ray.o + ray.d*ray.t

                intersectionNormal = 0
                if isinstance(ray.firstHitShape, Triangle)  :
                    v1v2 = ray.firstHitShape.v2 - ray.firstHitShape.v1
                    v1v3 = ray.firstHitShape.v3 - ray.firstHitShape.v1
                    intersectionNormal = np.cross(v1v3, v1v2)
                else :
                    # only for spheres
                    intersectionNormal = intersPoint

                # normalize normal vector
                intersectionNormal = intersectionNormal / np.linalg.norm(intersectionNormal)

                val = self.RandomStupidSampling(intersPoint, ray, scene, intersectionNormal)
                return val

        # no intersection so we stare into the deep void
        return [0.25,0.25,0.25]



    def BRDFSampling(self, intersectionPoint, ray, scene, intersectionNormal) :
        #todo
        return 0

    def LightSoureAreaSampling(self, intersectionPoint, ray, scene, intersectionNormal):
        #todo
        return 0

    def RandomStupidSampling(self, intersPoint, ray, scene, intersectionNormal):
        ############################################################## Prepare
        t0 = time.process_time()

        # all the light hitting our intersection point
        # this value is later normalized with the sample count
        # before that its just the sum of incoming light
        aquiredLightSum = 0

        # Array of light intensity value that goes into the integrator and the color
        # of the light [ (lightIntensity,[R,G,B]), ... ]
        aquiredLightsIntensity = np.zeros(MISIntegrator.sampleCount)
        aquiredLightsColor = np.zeros((MISIntegrator.sampleCount, 3))

        # filled out elements in the array
        aquiredLightsCount = 0

        # Calculate matrix that rotates from the default hemisphere normal
        # to the intersection normal
        sampleRoatationMatrix = self.rotation_matrix_numpy(np.cross(MISIntegrator.defaultHemisphereNormal, intersectionNormal) ,
                                            np.dot(MISIntegrator.defaultHemisphereNormal, intersectionNormal) * np.pi)

        debugRayList = []
        #if ray.firstHitShape.tri:
        #    ray.print2()

        MISIntegrator.TracePrepTime = time.process_time() - t0

        # integrate over sphere using monte carlo
        for sampleNr in range(MISIntegrator.sampleCount):
            ############################################################## Sample Rays
            t0 = time.process_time()
            lightSenseRay = Ray(intersPoint)

            #
            # sample generation
            #
            # generate direction of light sense ray shot away from the hemisphere

            # generate theta and phi
            theta = (np.random.random() * 2 - 1) * (np.pi / 2)
            phi = (np.random.random() * 2 - 1) * np.pi

            # map onto sphere
            # we get a point on the unit sphere that is oriented along the positive x axis
            lightSenseRaySecondPoint = self.twoAnglesTo3DPoint(theta, phi)

            # but because we need a sphere that is oriented along the intersection normal
            # we rotate the point with the precalculated sample rotation matrix
            lightSenseRaySecondPoint = np.dot(sampleRoatationMatrix, lightSenseRaySecondPoint)

            # to get direction for ray we aquire the vector from the intersection point to our adjusted point on
            # the sphere
            lightSenseRay.d = -lightSenseRaySecondPoint
            lightSenseRay.d = lightSenseRay.d / np.linalg.norm(lightSenseRay.d)

            #debugRayList.append(lightSenseRay)

            #if ray.firstHitShape.tri:
            #    lightSenseRay.print2(sampleNr+1)

            MISIntegrator.RayGenTimeSec = time.process_time() - t0

            # send ray on its way
            if scene.intersectLights(lightSenseRay) :
                # weigh light intensity by various factors
                aquiredLight = lightSenseRay.firstHitShape.lightIntensity

                # lambert light model (cos weighting)
                # perpendicular light has highest intensity
                #
                aquiredLight *= np.abs(np.dot(intersectionNormal,lightSenseRay.d))


                aquiredLightSum += aquiredLight

                aquiredLightsIntensity[aquiredLightsCount] = aquiredLight
                aquiredLightsColor[aquiredLightsCount] = lightSenseRay.firstHitShape.lightColor
                aquiredLightsCount += 1

        ############################################################## Calculate Light
        t0 = time.process_time()
        combinedLightColor = np.zeros(3)

        # avoid / 0 when no light was aquired
        if aquiredLightSum > 0 :
            #
            # calculate pixel color
            #

            # first calculate the color of the light hitting the shape
            # light that is more intense has more weight in the resulting color

            for n in range(aquiredLightsCount) :
                combinedLightColor += aquiredLightsColor[n] * (aquiredLightsIntensity[n] / aquiredLightSum)

            # should not be necessary
            combinedLightColor = util.clipColor(combinedLightColor)

            # normalize light
            aquiredLightSum /= MISIntegrator.sampleCount

            #if ray.firstHitShape.tri:
            #    for n in range(len(debugRayList)):
            #        debugRayList[n].print2(n)
        #else:
            """
            if ray.firstHitShape.tri:
                for n in range(len(debugRayList)):
                    debugRayList[n].print2(n)
            """
        #    return [0,1,0]

        MISIntegrator.ColorGenTimeSec = time.process_time() - t0

        # combine light color and object color + make it as bright as light that falls in
        return ray.firstHitShape.color * combinedLightColor * aquiredLightSum


    """
    theta, phi angles in radiant
    Returns vector from coordinate origin to point on unit sphere where both angles would put it
    """
    def twoAnglesTo3DPoint(self, theta, phi):
        r3 = np.zeros(3)
        r3[0] = np.sin(theta) * np.cos(phi)
        r3[1] = np.sin(theta) * np.sin(phi)
        r3[2] = np.cos(theta)
        return r3


    """
    Renerates rotation matrix from given axis and angle
    """
    def rotation_matrix_numpy(self, axis, theta):
        # https://stackoverflow.com/questions/6802577/python-rotation-of-3d-vector
        mat = np.eye(3, 3)
        axis = axis / np.sqrt(np.dot(axis, axis))
        a = np.cos(theta / 2.)
        b, c, d = -axis * np.sin(theta / 2.)

        return np.array([[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
                         [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
                         [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - b * b - c * c]])

