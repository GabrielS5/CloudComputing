using System;
using System.Linq;
using System.Threading.Tasks;
using TemaCC4.Database;
using TemaCC4.Models;

namespace TemaCC4.Services
{
    public class UsersService : IUsersService
    {
        private AppDbContext context;

        public UsersService(AppDbContext context)
        {
            this.context = context;
        }

        public async Task<bool> Authenticate(User user)
        {
            var dbUser = context.Users.FirstOrDefault(f => f.Id == user.Id);

            return dbUser != null;
        }

        public async Task<User> GetUserById(Guid id)
        {
            return context.Users.FirstOrDefault(f => f.Id == id);
        }

        public async Task<User> LogIn(User user)
        {
            var dbUser = context.Users.FirstOrDefault(f => f.Name == user.Name && f.Password == user.Password);

            return dbUser;
        }

        public async Task Register(User user)
        {
            var dbUser = context.Users.FirstOrDefault(f => f.Name == user.Name);

            if (dbUser == null)
            {
                await context.Users.AddAsync(user);

                await context.SaveChangesAsync();
            }

        }
    }
}
