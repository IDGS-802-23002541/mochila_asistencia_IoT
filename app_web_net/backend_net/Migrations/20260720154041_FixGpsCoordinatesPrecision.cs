using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CangureraInteligente.Migrations
{
    /// <inheritdoc />
    public partial class FixGpsCoordinatesPrecision : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "Operativo");

            migrationBuilder.CreateTable(
                name: "Cat_TiposEvento",
                schema: "Operativo",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    NombreEvento = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    Severidad = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Cat_TiposEvento", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Organizaciones",
                schema: "Operativo",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Nombre = table.Column<string>(type: "nvarchar(150)", maxLength: 150, nullable: false),
                    Sector = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    Contacto_Principal = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Email_Contacto = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    FechaCreacion = table.Column<DateTime>(type: "datetime2", nullable: false),
                    Estado_Activo = table.Column<bool>(type: "bit", nullable: false),
                    Contrasena_Hash = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    Rol = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    Es_Interna = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Organizaciones", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Dispositivos",
                schema: "Operativo",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    OrganizacionId = table.Column<int>(type: "int", nullable: false),
                    MacAddress = table.Column<string>(type: "nvarchar(17)", maxLength: 17, nullable: false, collation: "SQL_Latin1_General_CP1_CI_AS"),
                    FechaRegistro = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UltimaConexion = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Estado = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Dispositivos", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Dispositivos_Organizaciones_OrganizacionId",
                        column: x => x.OrganizacionId,
                        principalSchema: "Operativo",
                        principalTable: "Organizaciones",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Usuarios",
                schema: "Operativo",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    OrganizacionId = table.Column<int>(type: "int", nullable: false),
                    Nombre = table.Column<string>(type: "nvarchar(150)", maxLength: 150, nullable: false),
                    Correo = table.Column<string>(type: "nvarchar(150)", maxLength: 150, nullable: false),
                    Contrasena_Hash = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: false),
                    Rol = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    FechaRegistro = table.Column<DateTime>(type: "datetime2", nullable: false),
                    Estado_Activo = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Usuarios", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Usuarios_Organizaciones_OrganizacionId",
                        column: x => x.OrganizacionId,
                        principalSchema: "Operativo",
                        principalTable: "Organizaciones",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Recorridos",
                schema: "Operativo",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    DispositivoId = table.Column<int>(type: "int", nullable: false),
                    FechaInicio = table.Column<DateTime>(type: "datetime2", nullable: false),
                    FechaFin = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Recorridos", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Recorridos_Dispositivos_DispositivoId",
                        column: x => x.DispositivoId,
                        principalSchema: "Operativo",
                        principalTable: "Dispositivos",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Eventos_Detectados",
                schema: "Operativo",
                columns: table => new
                {
                    Id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    RecorridoId = table.Column<int>(type: "int", nullable: false),
                    TipoEventoId = table.Column<int>(type: "int", nullable: false),
                    TimestampEvento = table.Column<DateTime>(type: "datetime2", nullable: false),
                    Latitud = table.Column<decimal>(type: "decimal(9,6)", nullable: true),
                    Longitud = table.Column<decimal>(type: "decimal(9,6)", nullable: true),
                    Geo_Es_Estimado = table.Column<bool>(type: "bit", nullable: false),
                    FuerzaImpactoG = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    IrIzquierdo = table.Column<bool>(type: "bit", nullable: true),
                    IrDerecho = table.Column<bool>(type: "bit", nullable: true),
                    DistanciaCm = table.Column<decimal>(type: "decimal(7,2)", precision: 7, scale: 2, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Eventos_Detectados", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Eventos_Detectados_Cat_TiposEvento_TipoEventoId",
                        column: x => x.TipoEventoId,
                        principalSchema: "Operativo",
                        principalTable: "Cat_TiposEvento",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_Eventos_Detectados_Recorridos_RecorridoId",
                        column: x => x.RecorridoId,
                        principalSchema: "Operativo",
                        principalTable: "Recorridos",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "RecorridoCoordenadas",
                schema: "Operativo",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    RecorridoId = table.Column<int>(type: "int", nullable: false),
                    Fecha = table.Column<DateTime>(type: "datetime2", nullable: false),
                    Latitud = table.Column<decimal>(type: "decimal(9,6)", precision: 9, scale: 6, nullable: false),
                    Longitud = table.Column<decimal>(type: "decimal(9,6)", precision: 9, scale: 6, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_RecorridoCoordenadas", x => x.Id);
                    table.ForeignKey(
                        name: "FK_RecorridoCoordenadas_Recorridos_RecorridoId",
                        column: x => x.RecorridoId,
                        principalSchema: "Operativo",
                        principalTable: "Recorridos",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Cat_TiposEvento_NombreEvento",
                schema: "Operativo",
                table: "Cat_TiposEvento",
                column: "NombreEvento",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Dispositivos_MacAddress",
                schema: "Operativo",
                table: "Dispositivos",
                column: "MacAddress",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Dispositivos_OrganizacionId",
                schema: "Operativo",
                table: "Dispositivos",
                column: "OrganizacionId");

            migrationBuilder.CreateIndex(
                name: "IX_Eventos_Detectados_RecorridoId",
                schema: "Operativo",
                table: "Eventos_Detectados",
                column: "RecorridoId");

            migrationBuilder.CreateIndex(
                name: "IX_Eventos_Detectados_TipoEventoId",
                schema: "Operativo",
                table: "Eventos_Detectados",
                column: "TipoEventoId");

            migrationBuilder.CreateIndex(
                name: "IX_RecorridoCoordenadas_RecorridoId",
                schema: "Operativo",
                table: "RecorridoCoordenadas",
                column: "RecorridoId");

            migrationBuilder.CreateIndex(
                name: "IX_Recorridos_DispositivoId",
                schema: "Operativo",
                table: "Recorridos",
                column: "DispositivoId");

            migrationBuilder.CreateIndex(
                name: "IX_Usuarios_OrganizacionId",
                schema: "Operativo",
                table: "Usuarios",
                column: "OrganizacionId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Eventos_Detectados",
                schema: "Operativo");

            migrationBuilder.DropTable(
                name: "RecorridoCoordenadas",
                schema: "Operativo");

            migrationBuilder.DropTable(
                name: "Usuarios",
                schema: "Operativo");

            migrationBuilder.DropTable(
                name: "Cat_TiposEvento",
                schema: "Operativo");

            migrationBuilder.DropTable(
                name: "Recorridos",
                schema: "Operativo");

            migrationBuilder.DropTable(
                name: "Dispositivos",
                schema: "Operativo");

            migrationBuilder.DropTable(
                name: "Organizaciones",
                schema: "Operativo");
        }
    }
}
