using System;
using System.Drawing;
using Grasshopper;
using Grasshopper.Kernel;

namespace ClayPatterns
{
    public class ClayPatternsInfo : GH_AssemblyInfo
    {
        public override string Name => "ClayPatterns Info";

        //Return a 24x24 pixel bitmap to represent this GHA library.
        public override Bitmap Icon => null;

        //Return a short string describing the purpose of this GHA library.
        public override string Description => "";

        public override Guid Id => new Guid("AB49A24D-DFDC-4C52-82EA-3AE4D8C73541");

        //Return a string identifying you or your company.
        public override string AuthorName => "";

        //Return a string representing your preferred contact details.
        public override string AuthorContact => "";
    }
}