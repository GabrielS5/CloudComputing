using System;
using Microsoft.EntityFrameworkCore.Migrations;

namespace TemaCC4.Migrations
{
    public partial class AddedUsers : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<Guid>(
                name: "UserId",
                table: "PointsOfInterest",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "Users",
                columns: table => new
                {
                    Name = table.Column<string>(nullable: true),
                    Password = table.Column<string>(nullable: true),
                    Id = table.Column<Guid>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Users", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_PointsOfInterest_UserId",
                table: "PointsOfInterest",
                column: "UserId");

            migrationBuilder.AddForeignKey(
                name: "FK_PointsOfInterest_Users_UserId",
                table: "PointsOfInterest",
                column: "UserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_PointsOfInterest_Users_UserId",
                table: "PointsOfInterest");

            migrationBuilder.DropTable(
                name: "Users");

            migrationBuilder.DropIndex(
                name: "IX_PointsOfInterest_UserId",
                table: "PointsOfInterest");

            migrationBuilder.DropColumn(
                name: "UserId",
                table: "PointsOfInterest");
        }
    }
}
