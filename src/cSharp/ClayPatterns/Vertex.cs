using System;
using Rhino.Geometry;

namespace ClayPatterns
{
    public class Vertex
    {
        public int Index;
        public Point2d UVvalue;

        private Point3d originalLocation;
        private Point3d currenLocation;

        public Vector3d Normal;
        public Vector3d Tangent;
        public Vector3d Perpendicular;

        public Vertex()
        {
            this.setDefaultLocation();
            this.setDefaultMovements();
        }

        private void setDefaultLocation()
        {
            Index = 0;
            UVvalue = new Point2d(0.0, 0.0);
            originalLocation = new Point3d(0.0, 0.0, 0.0);
            currenLocation = new Point3d(0.0, 0.0, 0.0);
        }

        private void setDefaultMovements()
        {
            Normal = new Vector3d(1.0, 0.0, 0.0);
            Tangent = new Vector3d(0.0, 1.0, 0.0);
            Perpendicular = new Vector3d(0.0, 0.0, 1.0);
        }

        public Point3d Location
        {
            get { return currenLocation;  }
            set
            {
                originalLocation = value;
                currenLocation = new Point3d(value);
            }
        }

        public void MoveNormal(double value)
        {
            currenLocation.X += Normal.X * value;
            currenLocation.Y += Normal.Y * value;
            currenLocation.Z += Normal.Z * value;
        }

        public void MoveTangent(double value)
        {
            currenLocation.X += Tangent.X * value;
            currenLocation.Y += Tangent.Y * value;
            currenLocation.Z += Tangent.Z * value;
        }

        public void MovePerpendicular(double value)
        {
            currenLocation.X += Perpendicular.X * value;
            currenLocation.Y += Perpendicular.Y * value;
            currenLocation.Z += Perpendicular.Z * value;
        }

        public void Move(double value)
        {
            MoveNormal(value);
        }

        public void Move(double valueN, double valueT)
        {
            MoveNormal(valueN);
            MoveTangent(valueT);
        }

        public void Move(double valueN, double valueT, double valueP)
        {
            MoveNormal(valueN);
            MoveTangent(valueT);
            MovePerpendicular(valueP);
        }
    }
}
