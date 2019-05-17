using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using TemaCC4.Models;
using TemaCC4.Models.Json;

namespace TemaCC4.Services
{
    public class HttpService
    {
        public async Task<Location> GetLocation(string query)
        {
            Response data = null;
            string baseUrl = "https://atlas.microsoft.com/search/address/json?api-version=1.0&subscription-key=jafHlPTWuF0LcBMgiZiU8Sp8lSCOmUjnZ9lPpST7idw&query=" + query;

            using (HttpClient client = new HttpClient())

            using (HttpResponseMessage res = await client.GetAsync(baseUrl))
            using (HttpContent content = res.Content)
            {
                data = await content.ReadAsAsync<Response>();
            }

            Result firstResult = data.Results.FirstOrDefault();

            Location location = new Location()
            {
                Name = data.Summary.Query,
                Country = firstResult.Address.Country,
                CountryCode = firstResult.Address.CountryCode,
                Type = firstResult.EntityType,
                Latitude = firstResult.Position.Lat,
                Longitude = firstResult.Position.Lon
            };

            return location;
        }

    }
}
