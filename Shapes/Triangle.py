#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from Shapes.shape import Shape

# vertices are always given in CW order


class Triangle(Shape):
    def __init__(self,v1,v2,v3, color):

        super().__init__(color)
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.tri=True

    def intersect(self, ray):

        #compute planes`s normal

        v1v2=self.v2-self.v1
        v1v3=self.v3-self.v1
        n=np.cross(v1v2,v1v3)

        #Step 1: finding the intersection point with triangle plane

        #Check if plane and ray are parallel
        ndotRayDirection = np.dot(n,ray.d)
        if (np.fabs(ndotRayDirection)<0.001) :   #almost zero
            return False

        #compute d parameter
        d=np.dot(n,self.v1)

        #compute t (length of the ray at intersection point)
        t = (np.dot(n,ray.o)+d)/ndotRayDirection
        #check if triangle is behind ray
        if(t<0):
            return False

        #compute intersection point
        p=ray.o+t*ray.d

        #Step 2: check if p is inside the triangle
        #edge 1
        edge1=self.v2-self.v1
        v1p=p-self.v1
        c=np.cross(edge1,v1p) #vector perpendicular to triangle's plane (orthogonal)
        if(np.dot(n,c) < 0):
            return False #p is on the right side

        #edge 2
        edge2=self.v3-self.v2
        v2p=p-self.v2
        c=np.cross(edge2,v2p)
        if(np.dot(n,c) < 0):
            return False

        # edge 3
        edge3 = self.v1 - self.v3
        v3p = p - self.v3
        c = np.cross(edge3, v3p)
        if (np.dot(n, c) < 0):
            return False

        #check if triangle is out of range
        if(ray.t<t):
            ray.t=t
            return True

        """
        // Barycentric approach according to lecture slides
  // Ray: x=o+t*d
  // Barycentric Triangle: x=a*u+b*v+c*w
  // Solve: o+t*d = u*a+v*b+w*c

  // This is an inhomogeneous linear system
  // (ax bx cx -dx) (u) = ox
  // (ay by cy -dy) (v) = oy
  // (az bz cz -dz) (w) = oz
  // (1  1  1   0 ) (t) = 1

  // or in short: A*x = o
  // Then, solution is given by A^-1 * o = x
  // with x = (u,v,w,t)^T
  /*
  const Vec3& o = ray.origin();
  const Vec3& d = ray.direction();
  Mat4 A;
  A(0,0)=a[0];A(0,1)=b[0];A(0,2)=c[0];A(0,3)=-d[0];
  A(1,0)=a[1];A(1,1)=b[1];A(1,2)=c[1];A(1,3)=-d[1];
  A(2,0)=a[2];A(2,1)=b[2];A(2,2)=c[2];A(2,3)=-d[2];
  A(3,0)=1   ;A(3,1)=1   ;A(3,2)=1   ;A(3,3)=0;

  A.invert();
  Vec4 x=A*Vec4(o,1);

  uvw[0] = x[0];
  uvw[1] = x[1];
  uvw[2] = x[2];
  lambda = x[3];

  return true;
  */

  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////

  //Approach by Moeller and Trumbore
  //see Fast, Minimum Storage RayTriangle Intersection
  // Ray: x=o+t*d
  // Barycentric Triangle: x=u*a+v*b+w*c
  // w=1-u-v
  // Therefore
  // x=u*a+v*b+(1-u-v)*c
  // Solve: o+t*d = u*a+v*b+(1-u-v)*c
  // Rearrange, then
  // (ax-cx bx-cx -dx) (u) = (ox-dx)
  // (ay-cy by-cy -dy) (v) = (oy-dy)
  // (az-cz bz-cz -dz) (t) = (oz-dz)
  // or in short: A*x = b
  // Then, solution is given by A^-1 * b = x
  // with x = (u,v,t)^T

  // This system can be solved using Cramer's rule
  // x_i = det(A_i) / det(A)
  // where the i-th column is replaced with b in the Matrix A_i
  //
  // e1 = a-c
  // e2 = b-c
  // tt = o-d

  // then
  // (        ) (u)
  // (e1 e2 -d) (v) =  tt
  // (        ) (t)

  // with
  // (u)                    ( det(tt,e2,-d) )
  // (v) = 1/det(e1,e2,-d)* ( det(e1,tt,-d) )
  // (t)                    ( det(e1,e2,tt) )

  //use triple scalar product
  // det(a,b,c) = a * (b x c) = b * (c x a) = c*(a x b)  , and
  // a * (b x c) = -a * (c x b)

  // then
  // (u)                    ( tt * (e2 x -d) )
  // (v) = e1*(e2 x -d)     ( e1 * (tt x -d) )
  // (t)                    ( e1 * (e2 x tt) )

  //rearrange terms for u,t
  // (u)                    ( tt * (e2 x -d) )
  // (v) = e1*(e2 x -d)     ( -d * (e1 x tt) )
  // (t)                    (-e2 * (e1 x tt) )
  // reuse expensive terms
  // pp = e2 x -d
  // qq = e1 x tt
  // then
  // (u)                    ( tt * pp )
  // (v) = e1*pp            ( -d * qq )
  // (t)                    (-e2 * qq )

    const Vec3d& o = ray.origin();
    const Vec3d& d = ray.direction();
    Vec3d e1 = a-c;
    Vec3d e2 = b-c;
    Vec3d tt = o-c;
    Vec3d pp = cross(e2,-d);
    Vec3d qq = cross(e1,tt);

    double detA = dot(e1,pp);

    if(fabs(detA) < Math::safetyEps())
      return false;

    uvw[0] = (dot( tt,pp))/detA;
    uvw[1] = (dot( -d,qq))/detA;
    uvw[2] = 1-uvw[0]-uvw[1];
    lambda = (dot(-e2,qq))/detA;

    return true;

  }

        """
        return False


