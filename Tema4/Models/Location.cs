using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TemaCC4.Models
{
    public class Location
    {
        public Guid Id { get; set; }
        public string Name { get; set; }
        public string Type { get; set; }
        public double Latitude { get; set; }
        public double Longitude { get; set; }
        public string Country { get; set; }
        public string CountryCode { get; set; }
    }
}
