using System;

namespace TemaCC4.Models
{
    public class PointOfInterest
    {
        public Guid Id { get; set; }

        public double Latitude { get; set; }

        public double Longitude { get; set; }

        public string Name { get; set; }

        public string Type { get; set; }

        public User User { get; set; }
    }
}
