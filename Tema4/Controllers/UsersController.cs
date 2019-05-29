using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using TemaCC4.Models;
using TemaCC4.Services;

namespace TemaCC4.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class UsersController : ControllerBase
    {
        private IUsersService usersService;

        public UsersController(IUsersService usersService)
        {
            this.usersService = usersService;
        }

        [HttpGet("login")]
        public async Task<ActionResult<User>> LogIn([FromQuery]User user)
        {
            return await usersService.LogIn(user);
        }

        [HttpGet("authenticate")]
        public async Task<ActionResult<bool>> Authenticate([FromQuery]User user)
        {
            return await usersService.Authenticate(user);
        }

        [HttpPost("register")]
        public async Task<ActionResult<User>> Register([FromQuery]User user)
        {
            await usersService.Register(user);

            return user;
        }
    }
}
