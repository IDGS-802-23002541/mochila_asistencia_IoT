using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CangureraInteligente.Migrations
{
    /// <inheritdoc />
    public partial class AgregarComentarios : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Comentarios",
                schema: "Operativo",
                columns: table => new
                {
                    IdComentario = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    NombreCliente = table.Column<string>(type: "nvarchar(150)", maxLength: 150, nullable: false),
                    CorreoCliente = table.Column<string>(type: "nvarchar(150)", maxLength: 150, nullable: false),
                    Mensaje = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: false),
                    FechaCreacion = table.Column<DateTime>(type: "datetime2", nullable: false),
                    Estado = table.Column<string>(type: "nvarchar(30)", maxLength: 30, nullable: false),
                    RespuestaAdministrador = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    FechaRespuesta = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Comentarios", x => x.IdComentario);
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Comentarios",
                schema: "Operativo");
        }
    }
}