using System;
using System.Collections.Generic;

using Grasshopper;
using Grasshopper.Kernel;
using Rhino.Geometry;

namespace ClayPrinting
{
    public class CrvToMesh
    {
        public List<Point3d> VertexPoints = new List<Point3d>();
        public List<int[]> FacesList = new List<int[]>();
        public int Count;
        public double Spacing;
        public double LayerHeight;
        public int LayerCount;
        public Curve BaseCurve;

        public CrvToMesh(Curve baseCurve, double spacing = 1.00, double layerHeight = 2.5, int layerCount = 20)
        {
            BaseCurve = baseCurve;
            Spacing = spacing;
            LayerHeight = layerHeight;
            LayerCount = layerCount;

            Count = Convert.ToInt32(baseCurve.GetLength() / spacing);
        }

        private List<Point3d> divideBaseCurve(int inputCount)
        {
            double[] ts = BaseCurve.DivideByCount(inputCount, true);
            List<Point3d> outputList = new List<Point3d>();
            foreach (double t in ts)
            {
                outputList.Add(BaseCurve.PointAt(t));
            }
            return outputList;
        }

        private List<List<Point3d>> triangularBasePoints()
        {
            List<Point3d> tmpList = divideBaseCurve(Count * 2);

            List<List<Point3d>> outputList = new List<List<Point3d>>();
            outputList.Add(new List<Point3d>());
            outputList.Add(new List<Point3d>());

            int idx = 0;
            foreach (Point3d pt in tmpList)
            {
                outputList[idx % 2].Add(pt);
                idx++;
            }

            if (BaseCurve.IsClosed)
            {
                Console.WriteLine("curve is closed, I do f'all");
            }
            else
            {
                outputList[1].Insert(0, outputList[0][0]);
                int index = outputList[0].Count - 1;
                outputList[1].Add(outputList[0][index]);
            }

            Console.WriteLine("basePoints in 0: {0}", outputList[0].Count);
            Console.WriteLine("basePoints in 1: {0}", outputList[1].Count);

            return outputList;
        }

        private void triangularVertexes()
        {
            List<List<Point3d>> bPointLists = triangularBasePoints();

            for (int i = 0; i < LayerCount; i++)
            {
                double z = i * LayerHeight;

                foreach (Point3d pt in bPointLists[i%2])
                {
                    VertexPoints.Add(new Point3d(pt.X, pt.Y, z));
                }
            }
        }

        private void squareVertexes()
        {
            List<Point3d> tmpList = divideBaseCurve(Count);

            for (int i = 0; i < LayerCount; i++)
            {
                double z = i * LayerHeight;

                foreach (Point3d pt in tmpList)
                {
                    VertexPoints.Add(new Point3d(pt.X, pt.Y, z));
                }
            }
        }

        public Point3d heightCalculation(double x, double y, int layerCount)
        {
            return new Point3d(x, y, layerCount * LayerHeight);
        }

        private void triangularVertexesHeights()
        {
            List<List<Point3d>> bPointLists = triangularBasePoints();
            for (int i = 0; i < LayerCount; i++)
            {
                foreach (Point3d pt in bPointLists[i % 2])
                {
                    VertexPoints.Add(heightCalculation(pt.X, pt.Y, i));
                }
            }
        }

        private void squareVertexesHeights()
        {
            List<Point3d> tmpList = divideBaseCurve(Count);

            for (int i = 0; i < LayerCount; i++)
            {
                foreach (Point3d pt in tmpList)
                {
                    VertexPoints.Add(heightCalculation(pt.X, pt.Y, i));
                }
            }
        }

        private void triangularFaces()
        {
            FacesList = new List<int[]>();

            if (BaseCurve.IsClosed)
            {
                for (int j = 0; j < LayerCount - 1; j++)
                {
                    int j_a = j * Count;
                    int j_b = j_a + Count;

                    if (j % 2 == 1)
                    {
                        for (int i = 0; i < Count - 1; i++)
                        {
                            int i_b = i + 1;
                            int a = j_a + i;
                            int b = j_a + i_b;
                            int c = j_b + i_b;
                            int d = j_b + i;

                            int[] fListA = new int[] { a, c, d };
                            int[] fListB = new int[] { a, b, c };

                            FacesList.Add(fListA);
                            FacesList.Add(fListB);
                        }

                        int b_end = j_a + Count - 1;
                        int c_end = j_b + Count - 1;

                        int[] finalListA = new int[] { b_end, j_a, j_b };
                        int[] finalListB = new int[] { j_b, c_end, b_end };

                        FacesList.Add(finalListA);
                        FacesList.Add(finalListB);
                    }

                    else
                    {
                        for (int i = 0; i < Count - 1; i++)
                        {
                            int i_b = i + 1;
                            int a = j_a + i;
                            int b = j_a + i_b;
                            int c = j_b + i_b;
                            int d = j_b + i;

                            int[] fListA = new int[] { a, b, d };
                            int[] fListB = new int[] { b, c, d };

                            FacesList.Add(fListA);
                            FacesList.Add(fListB);
                        }

                        int b_end = j_a + Count - 1;
                        int c_end = j_b + Count - 1;

                        int[] finalListA = new int[] { b_end, j_a, c_end };
                        int[] finalListB = new int[] { j_b, c_end, j_a };

                        FacesList.Add(finalListA);
                        FacesList.Add(finalListB);
                    }
                }
            }
            else
            {
                int j_b = 0;

                for (int j = 0; j < LayerCount - 1; j++)
                {
                    int j_a = j_b;

                    if (j % 2 == 1)
                    {
                        j_b += Count + 2;
                        for (int i = 0; i < Count; i++)
                        {
                            int i_b = i + 1;
                            int a = j_a + i;
                            int b = j_a + i_b;
                            int c = j_b + i_b;
                            int d = j_b + i;

                            int[] fListA = new int[] { a, b, d };
                            int[] fListB = new int[] { b, c, d };

                            FacesList.Add(fListA);
                            FacesList.Add(fListB);
                        }

                        int b_end = j_a + Count;
                        int c_end = j_b + Count;

                        int[] finalList = new int[] { b_end, c_end, b_end + 1};

                        FacesList.Add(finalList);
                    }

                    else
                    {
                        j_b += Count + 1;
                        for (int i = 0; i < Count; i++)
                        {
                            int i_b = i + 1;
                            int a = j_a + i;
                            int b = j_a + i_b;
                            int c = j_b + i_b;
                            int d = j_b + i;

                            int[] fListA = new int[] { a, b, c };
                            int[] fListB = new int[] { a, c, d };

                            FacesList.Add(fListA);
                            FacesList.Add(fListB);
                        }

                        int b_end = j_a + Count;
                        int c_end = j_b + Count;

                        int[] finalList = new int[] { b_end, c_end, c_end + 1 };

                        FacesList.Add(finalList);
                    }
                }
            }
        }

        private void squareFaces()
        {
            FacesList = new List<int[]>();

            int actualCount = Count;
            if (BaseCurve.IsClosed);
            else actualCount += 1;

            int j_b = 0;

            for (int j = 0; j < LayerCount - 1; j++)
            {
                int j_a = j_b;
                j_b += actualCount;

                for (int i = 0; i < actualCount - 1; i++)
                {
                    int i_b = i + 1;
                    int a = j_a + i;
                    int b = j_a + i_b;
                    int c = j_b + i_b;
                    int d = j_b + i;

                    int[] fListA = new int[] { a, b, c };
                    int[] fListB = new int[] { c, d, a };

                    FacesList.Add(fListA);
                    FacesList.Add(fListB);

                }

                if (BaseCurve.IsClosed)
                {
                    int b_end = j_a + Count - 1;
                    int c_end = j_b + Count - 1;

                    int[] finalListA = new int[] { b_end, j_a, j_b };
                    int[] finalListB = new int[] { j_b, c_end, b_end };

                    FacesList.Add(finalListA);
                    FacesList.Add(finalListB);
                }
            }
        }

        private Mesh makeMesh()
        {
            Mesh outputMesh = new Mesh();

            foreach (Point3d v in VertexPoints)
            {
                outputMesh.Vertices.Add(v);
            }

            foreach (int[] fs in FacesList)
            {
                outputMesh.Faces.AddFace(fs[0], fs[1], fs[2]);
            }

            return outputMesh;
        }

        public Mesh SquareMesh()
        {
            squareVertexes();
            squareFaces();

            return makeMesh();
        }

        public Mesh SquareMeshHeights()
        {
            squareVertexesHeights();
            squareFaces();

            return makeMesh();
        }

        public Mesh TriangularMesh()
        {
            triangularVertexes();
            triangularFaces();

            return makeMesh();
        }

        public Mesh TriangularMeshHeights()
        {
            triangularVertexesHeights();
            triangularFaces();

            return makeMesh();
        }
    }
}
