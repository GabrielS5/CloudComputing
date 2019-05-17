using System.Collections.Generic;

namespace TemaCC4.Models.Json
{
    public class Response
    {
        public Summary Summary { get; set; }
        public List<Result> Results { get; set; }
    }

    public class Summary
    {
        public string Query { get; set; }
    }
}
