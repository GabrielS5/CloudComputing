namespace TemaCC4.Models.Json
{
    public class Result
    {
        public string EntityType { get; set; }
        public Address Address { get; set; }
        public Position Position { get; set; }

    }

    public class Address
    {
        public string CountryCode { get; set; }
        public string Country { get; set; }
    }

    public class Position
    {
        public double Lat { get; set; }
        public double Lon { get; set; }
    }
}