using System;
using System.Linq;
using TemaCC4.Database;
using TemaCC4.Models;

namespace TemaCC4.Services
{
    public class LocationsService : ILocationsService
    {
        private AppDbContext context;

        public LocationsService(AppDbContext context)
        {
            this.context = context;
        }

        public void AddLocation(Location location)
        {
            context.Locations.Add(location);
            context.SaveChanges();
        }

        public Location GetLocation(string name)
        {
            return context.Locations.FirstOrDefault(f => f.Name.ToLower() == name.ToLower());
        }
    }
}
