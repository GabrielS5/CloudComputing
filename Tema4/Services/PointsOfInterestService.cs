using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TemaCC4.Database;
using TemaCC4.Models;

namespace TemaCC4.Services
{
    public class PointsOfInterestService : IPointsOfInterestService
    {
        private AppDbContext context;

        public PointsOfInterestService(AppDbContext context)
        {
            this.context = context;
        }

        public async Task Add(PointOfInterest pointOfInterest)
        {
            await context.PointsOfInterest.AddAsync(pointOfInterest);

            await context.SaveChangesAsync();
        }

        public async Task Delete(PointOfInterest pointOfInterest)
        {
            var dbItem = await GetById(pointOfInterest.Id);

            context.PointsOfInterest.Remove(dbItem);

            await context.SaveChangesAsync();
        }

        public async Task<IEnumerable<PointOfInterest>> GetAll()
        {
            return context.PointsOfInterest.AsEnumerable();
        }

        public async Task<PointOfInterest> GetById(Guid id)
        {
            return context.PointsOfInterest.FirstOrDefault(f => f.Id == id);
        }
    }
}
