using Microsoft.EntityFrameworkCore;
using TemaCC4.Models;

namespace TemaCC4.Database
{
    public sealed class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options)
            : base(options)
        {
            Database.Migrate();
        }

        public DbSet<Location> Locations { get; set; }

        public DbSet<PointOfInterest> PointsOfInterest { get; set; }

        public DbSet<User> Users { get; set; }
    }
}
