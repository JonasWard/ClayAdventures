using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using System.Collections.Generic;

using System;
namespace ClayPatterns
{
    public class BasePatternClass : GH_Goo<int>
    {
        private bool isValid = false;
        public BasePatternClass()
        {
        }

        public BasePatternClass(int internal_data) : base(internal_data)
        {
        }

        public BasePatternClass(GH_Goo<int> other) : base(other)
        {
        }

        public override bool IsValid
        {
            get { return this.isValid; }
        }

        public override string TypeName
        {
            get { return "BasePattern"; }
        }

        public override string TypeDescription
        {
            get { return "A pattern type"; }
        }

        public override IGH_Goo Duplicate()
        {
            throw new NotImplementedException();
        }

        public override string ToString()
        {
            return "CCCL - empty pattern type";
        }

        public List<Vertex> PatternMap(List<Vertex> inputVertices)
        {
            return inputVertices;
        }
    }

    public class SineWave : BasePatternClass
    {
        public double Phase;
        public double Period;
        public double Amplitude;
        public double Shift;

        private bool shiftSet = false;
        public bool NormalShift = true;
        public bool PerpendicularShift = false;
        public bool TangentShift = false;

        public SineWave(double phase, double period, double amplitude, double shift)
        {
            Phase = phase;
            Period = period;
            Amplitude = amplitude;
            Shift = shift * period;

            if (Math.Abs(Shift) < .0001) {
                shiftSet = false;
            }
        }

        public override string ToString()
        {
            string ccclOutput = "CCCL - Sine wave pattern type" + "\n" +
                                "        Phase     : " + Phase + "\n" +
                                "        Period    : " + Period + "\n" +
                                "        Amplitude : " + Amplitude + "\n" +
                                "        Shift     : ";
            if (shiftSet) { ccclOutput = ccclOutput + Shift; }
            else { ccclOutput = ccclOutput + "none"; }

            return ccclOutput;
        }

        private double SinePhaseFunction(double uValue, double vValue)
        {
            return Math.Sin(uValue / Period + Phase + vValue / Shift) * Amplitude;
        }

        private double SineFunction(double uValue)
        {
            return Math.Sin(uValue / Period + Phase) * Amplitude;
        }
    }

    public class SineWave2D : SineWave
    {
        public SineWave2D(double phase, double period, double amplitude, double shift) : base(phase, period, amplitude, shift) { }

        public override IGH_Goo Duplicate()
        {
            return this.CreateDuplicate();
        }

        public SineWave2D CreateDuplicate()
        {
            SineWave2D duplicateSW = new SineWave2D(Phase, Period, Amplitude, Shift);

            duplicateSW.NormalShift = NormalShift;
            duplicateSW.PerpendicularShift = PerpendicularShift;
            duplicateSW.TangentShift = TangentShift;

            return duplicateSW;
        }

        private SineWave2D MakePeriodic(double DomainLength)
        {
            SineWave2D periodicSW = this.CreateDuplicate();
            periodicSW.Period = DomainLength / Math.Round(DomainLength / Period);
            return periodicSW;
        }

        //public SineWave2D MakePeriodic(ShellObject shell)
        //{

        //}
    }
}
