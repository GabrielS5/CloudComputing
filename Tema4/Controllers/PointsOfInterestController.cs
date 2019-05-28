using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TemaCC4.Models;
using TemaCC4.Services;

namespace TemaCC4.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class PointsOfInterestController : ControllerBase
    {
        private IPointsOfInterestService pointsOfInterestService;

        public PointsOfInterestController(IPointsOfInterestService pointsOfInterestService)
        {
            this.pointsOfInterestService = pointsOfInterestService;
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<PointOfInterest>> Get(Guid id)
        {
            return Ok(await pointsOfInterestService.GetById(id));
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<PointOfInterest>>> GetAll()
        {
            return Ok(await pointsOfInterestService.GetAll());
        }

        [HttpPost]
        public async Task<ActionResult<Location>> Post([FromQuery]PointOfInterest pointOfInterest)
        {
            await pointsOfInterestService.Add(pointOfInterest);

            return Ok();
        }

        [HttpDelete]
        public async Task<ActionResult<Location>> Delete([FromQuery]PointOfInterest pointOfInterest)
        {
            await pointsOfInterestService.Delete(pointOfInterest);

            return Ok();
        }
    }
}