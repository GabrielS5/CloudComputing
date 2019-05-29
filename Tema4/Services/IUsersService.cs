using System;
using System.Threading.Tasks;
using TemaCC4.Models;

namespace TemaCC4.Services
{
    public interface IUsersService
    {
        Task Register(User user);

        Task<bool> Authenticate(User user);

        Task<User> LogIn(User user);

        Task<User> GetUserById(Guid id);
    }
}
