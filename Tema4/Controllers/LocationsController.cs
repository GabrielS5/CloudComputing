﻿using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using TemaCC4.Models;
using TemaCC4.Services;

namespace TemaCC4.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class LocationsController : ControllerBase
    {
        private HttpService httpService;
        private ILocationsService locationsService;

        public LocationsController(ILocationsService locationsService)
        {
            httpService = new HttpService();
            this.locationsService = locationsService;
        }

        [HttpGet]
        public async Task<ActionResult<Location>> Get([FromQuery]string query)
        {
            if (string.IsNullOrEmpty(query))
                return null;

            var location = this.locationsService.GetLocation(query);

            if (location == null)
            {
                location = await httpService.GetLocation(query);
                locationsService.AddLocation(location);
            }

            return location;
        }
    }
}
