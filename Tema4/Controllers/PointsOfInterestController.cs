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
        private IUsersService usersService;

        public PointsOfInterestController(IPointsOfInterestService pointsOfInterestService, IUsersService usersService)
        {
            this.pointsOfInterestService = pointsOfInterestService;
            this.usersService = usersService;
        }

        [HttpGet("{userId}")]
        public async Task<ActionResult<IEnumerable<PointOfInterest>>> GetAll(Guid userId)
        {
            var isAuthenticated = await usersService.Authenticate(new User { Id = userId });

            if (!isAuthenticated)
                return Forbid();

            var results = await pointsOfInterestService.GetAll();

            results = results.Where(w => w.User != null &&  w.User.Id == userId);

            return Ok(results);
        }

        [HttpPost("{userId}")]
        public async Task<ActionResult<Location>> Post(Guid userId, [FromQuery]PointOfInterest pointOfInterest)
        {
            var isAuthenticated = await usersService.Authenticate(new User { Id = userId });

            if (!isAuthenticated)
                return Forbid();

            var user = await usersService.GetUserById(userId);

            pointOfInterest.User = user;

            await pointsOfInterestService.Add(pointOfInterest);

            return Ok();
        }

        [HttpDelete("{userId}")]
        public async Task<ActionResult<Location>> Delete(Guid userId, [FromQuery]PointOfInterest pointOfInterest)
        {
            var isAuthenticated = await usersService.Authenticate(new User { Id = userId });

            if (!isAuthenticated)
                return Forbid();

            await pointsOfInterestService.Delete(pointOfInterest);

            return Ok();
        }
    }
}