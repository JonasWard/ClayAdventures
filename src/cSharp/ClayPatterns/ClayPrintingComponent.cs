using System;
using System.Collections.Generic;

using Grasshopper;
using Grasshopper.Kernel;
using Rhino.Geometry;

namespace ClayPrinting
{
    public class ClayPrintingComponent : GH_Component
    {
        public ClayPrintingComponent()
          : base("ShellFromBaseCurve", "CCrv",
            "Construct a shell object from a given base curve",
            "CCCL", "Primitives")
        {
        }

        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddCurveParameter("Curve", "C", "BaseCurve", GH_ParamAccess.item);
            pManager.AddNumberParameter("Resolution Spacing", "S", "Sample length of the curve", GH_ParamAccess.item, 2.5);
            pManager.AddIntegerParameter("LayerCount", "Lc", "Total amount ", GH_ParamAccess.item, 15);
            pManager.AddNumberParameter("LayerHeight", "Lh", "Layer height", GH_ParamAccess.item, 2.5);
            pManager.AddBooleanParameter("AlternatingPoints", "Ap", "Whether the points are above each other or alternating", GH_ParamAccess.item, true);
        }

        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddMeshParameter("VisualisationMesh", "VMesh", "A mesh reppresentation of the generated point cloud", GH_ParamAccess.item);
            //pManager.AddParameter(dgsdhg,"Mesh2CurveObject", "M2Cobj", "the object that should be past around", GH_ParamAccess.item);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Curve bCurve = new LineCurve(new Point3d(0.0,0.0,0.0), new Point3d(1.0, 0.0, 0.0) );
            double spacing = 0.0;
            double layerHeight = 0.0;
            int layerCount = 0;
            bool triangle = false;

            if (!DA.GetData(0, ref bCurve)) return;
            if (!DA.GetData(1, ref spacing)) return;
            if (!DA.GetData(2, ref layerCount)) return;
            if (!DA.GetData(3, ref layerHeight)) return;
            if (!DA.GetData(4, ref triangle)) return;

            CrvToMesh curveShellObject = new CrvToMesh(bCurve, spacing, layerHeight, layerCount);
            Mesh meshVisualisation;
            if (triangle)
            {
                meshVisualisation = curveShellObject.TriangularMesh();
            }
            else
            {
                meshVisualisation = curveShellObject.SquareMesh();
            }

            DA.SetData(0, meshVisualisation);
            //DA.SetData(1, curveShellObject);
        }
        public override GH_Exposure Exposure => GH_Exposure.primary;

        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                return null;
            }
        }
        public override Guid ComponentGuid => new Guid("1C2BE8E9-A945-4819-A9E2-3EE2830F7000");
    }
}