using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using TemaCC4.Models;

namespace TemaCC4.Services
{
    public interface IPointsOfInterestService
    {
        Task Add(PointOfInterest pointOfInterest);
        Task Delete(PointOfInterest pointOfInterest);
        Task<IEnumerable<PointOfInterest>> GetAll();
        Task<PointOfInterest> GetById(Guid id);
    }
}
