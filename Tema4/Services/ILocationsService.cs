using TemaCC4.Models;

namespace TemaCC4.Services
{
    public interface ILocationsService
    {
        Location GetLocation(string name);
        void AddLocation(Location location);
    }
}
