-- #############################################################################
-- # KAIROS BCP - ESQUEMA DE BASE DE DATOS INICIAL                             #
-- #############################################################################

-- #############################################################################
-- # 1. EXTENSIONES
-- # Habilitar extensiones necesarias.
-- #############################################################################

CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Para generar UUIDs (ej. uuid_generate_v4())
CREATE EXTENSION IF NOT EXISTS "vector";    -- Para el tipo de dato VECTOR (pgvector)

-- #############################################################################
-- # 2. FUNCIÓN PARA ACTUALIZAR TIMESTAMPS
-- # Función para actualizar automáticamente el campo 'updated_at'.
-- #############################################################################

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- #############################################################################
-- # 3. DEFINICIÓN DE TABLAS
-- #############################################################################

-- -----------------------------------------------------------------------------
-- Tabla: user_profiles
-- Almacena los perfiles de los usuarios.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "user_profiles" (
    "user_id" TEXT PRIMARY KEY,
    "name" TEXT NULL,
    "email" TEXT UNIQUE NULL, -- Considerar añadir email para unicidad o notificaciones
    "preferences" JSONB NULL,
    "learned_context" JSONB NULL,
    "created_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    "updated_at" TIMESTAMPTZ DEFAULT now() NOT NULL
);

COMMENT ON TABLE "user_profiles" IS 'Almacena los perfiles de los usuarios y sus preferencias.';
COMMENT ON COLUMN "user_profiles"."user_id" IS 'Identificador único del usuario (puede provenir de un sistema de autenticación externo).';
COMMENT ON COLUMN "user_profiles"."preferences" IS 'Preferencias del usuario en formato JSONB (ej. tema UI, configuraciones por defecto).';
COMMENT ON COLUMN "user_profiles"."learned_context" IS 'Contexto aprendido sobre el usuario para personalizar la experiencia (ej. con IA).';

-- Trigger para updated_at en user_profiles
CREATE OR REPLACE TRIGGER set_timestamp_user_profiles
BEFORE UPDATE ON "user_profiles"
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- -----------------------------------------------------------------------------
-- Tabla: projects
-- Permite organizar las notas en proyectos, con soporte para jerarquías.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "projects" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" TEXT NOT NULL REFERENCES "user_profiles"("user_id") ON DELETE CASCADE,
    "name" TEXT NOT NULL,
    "description" TEXT NULL,
    "parent_project_id" UUID NULL REFERENCES "projects"("id") ON DELETE SET NULL,
    "created_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    "updated_at" TIMESTAMPTZ DEFAULT now() NOT NULL
);

COMMENT ON TABLE "projects" IS 'Permite organizar las notas en proyectos, con soporte para jerarquías.';
COMMENT ON COLUMN "projects"."parent_project_id" IS 'ID del proyecto padre para crear jerarquías.';

-- Trigger para updated_at en projects
CREATE OR REPLACE TRIGGER set_timestamp_projects
BEFORE UPDATE ON "projects"
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- -----------------------------------------------------------------------------
-- Tabla: sources
-- Rastrea el origen de la información de las notas (URLs, libros, etc.).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "sources" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" TEXT NOT NULL REFERENCES "user_profiles"("user_id") ON DELETE CASCADE,
    "type" VARCHAR(100) NULL,
    "title" TEXT NULL,
    "description" TEXT NULL,
    "url" TEXT NULL,
    "link_metadata" JSONB NULL,
    "created_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    "updated_at" TIMESTAMPTZ DEFAULT now() NOT NULL
);

COMMENT ON TABLE "sources" IS 'Rastrea el origen de la información de las notas (URLs, libros, etc.).';
COMMENT ON COLUMN "sources"."type" IS 'Tipo de fuente, ej: website, book, article, video.';
COMMENT ON COLUMN "sources"."link_metadata" IS 'Metadatos adicionales en JSONB, específicos del tipo de fuente (ej. autor, ISBN para libros).';


-- Trigger para updated_at en sources
CREATE OR REPLACE TRIGGER set_timestamp_sources
BEFORE UPDATE ON "sources"
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- -----------------------------------------------------------------------------
-- Tabla: notes
-- Tabla central para almacenar las notas o unidades de conocimiento.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "notes" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" TEXT NOT NULL REFERENCES "user_profiles"("user_id") ON DELETE CASCADE,
    "project_id" UUID NULL REFERENCES "projects"("id") ON DELETE SET NULL,
    "source_id" UUID NULL REFERENCES "sources"("id") ON DELETE SET NULL,
    "title" TEXT NULL,
    "content" TEXT NOT NULL,
    "type" VARCHAR(100) NULL, -- Ej: 'QuickNote', 'ArticleSummary', 'MeetingMinutes', 'Idea'
    -- "embedding" VECTOR(768) NULL, -- Se añadirá en el futuro. Dimensión según modelo (ej. 768 para text-embedding-ada-002, 1536 para otros)
    "note_metadata" JSONB NULL,
    "created_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    "updated_at" TIMESTAMPTZ DEFAULT now() NOT NULL
);

COMMENT ON TABLE "notes" IS 'Tabla central para almacenar las notas o unidades de conocimiento.';
COMMENT ON COLUMN "notes"."type" IS 'Tipo principal de la nota para categorización y comportamiento, ej: QuickNote, ArticleSummary.';
COMMENT ON COLUMN "notes"."content" IS 'Contenido principal de la nota, podría ser Markdown, texto plano, etc.';
-- COMMENT ON COLUMN "notes"."embedding" IS 'Vector de embedding para búsqueda semántica (se añadirá en el futuro).';
COMMENT ON COLUMN "notes"."note_metadata" IS 'Metadatos adicionales en JSONB (ej. estado, prioridad, datos específicos del tipo de nota).';

-- Trigger para updated_at en notes
CREATE OR REPLACE TRIGGER set_timestamp_notes
BEFORE UPDATE ON "notes"
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- -----------------------------------------------------------------------------
-- Tabla: keywords
-- Almacena las palabras clave o tags definidas por el usuario.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "keywords" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" TEXT NOT NULL REFERENCES "user_profiles"("user_id") ON DELETE CASCADE,
    "name" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT "keywords_user_id_name_key" UNIQUE ("user_id", "name")
);

COMMENT ON TABLE "keywords" IS 'Almacena las palabras clave o tags definidas por el usuario.';
COMMENT ON COLUMN "keywords"."name" IS 'El texto de la palabra clave, único por usuario.';

-- -----------------------------------------------------------------------------
-- Tabla: note_keywords (Tabla de Unión Many-to-Many)
-- Asocia notas con palabras clave.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "note_keywords" (
    "note_id" UUID NOT NULL REFERENCES "notes"("id") ON DELETE CASCADE,
    "keyword_id" UUID NOT NULL REFERENCES "keywords"("id") ON DELETE CASCADE,
    PRIMARY KEY ("note_id", "keyword_id")
);

COMMENT ON TABLE "note_keywords" IS 'Tabla de unión para asociar notas con múltiples palabras clave (tags).';

-- -----------------------------------------------------------------------------
-- Tabla: note_links (Tabla de Unión Many-to-Many)
-- Crea enlaces tipados entre notas para formar una red de conocimiento.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "note_links" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Clave primaria para la relación en sí misma
    "source_note_id" UUID NOT NULL REFERENCES "notes"("id") ON DELETE CASCADE,
    "target_note_id" UUID NOT NULL REFERENCES "notes"("id") ON DELETE CASCADE,
    "link_type" VARCHAR(100) DEFAULT 'related' NULL, -- Ej: 'related', 'supports', 'refutes', 'parent_of', 'child_of'
    "description" TEXT NULL, -- Opcional: descripción del enlace
    "user_id" TEXT NOT NULL REFERENCES "user_profiles"("user_id") ON DELETE CASCADE, -- Para asegurar que el enlace es del mismo usuario que las notas
    "created_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT "note_links_source_target_user_key" UNIQUE ("source_note_id", "target_note_id", "user_id", "link_type"), -- Evita enlaces duplicados exactos
    CONSTRAINT "note_links_check_different_notes" CHECK ("source_note_id" <> "target_note_id") -- Una nota no puede enlazarse a sí misma con este constraint
);

COMMENT ON TABLE "note_links" IS 'Crea enlaces tipados entre notas para formar una red de conocimiento.';
COMMENT ON COLUMN "note_links"."link_type" IS 'Tipo de relación entre la nota origen y la nota destino.';
COMMENT ON COLUMN "note_links"."user_id" IS 'Usuario propietario del enlace, debe coincidir con el de las notas enlazadas.';


-- -----------------------------------------------------------------------------
-- Tabla: templates
-- Almacena plantillas para la creación de notas.
-- -----------------------------------------------------------------------------
/*
CREATE TABLE IF NOT EXISTS "templates" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" TEXT NOT NULL REFERENCES "user_profiles"("user_id") ON DELETE CASCADE,
    "name" TEXT NOT NULL,
    "description" TEXT NULL,
    "content_structure" JSONB NULL, -- Estructura de contenido, ej. { "title_template": "Resumen de {{source_title}}", "sections": [{"header": "Puntos Clave", "placeholder": "Añade puntos clave aquí..."}] }
    "default_note_type" VARCHAR(100) NULL,
    "default_metadata" JSONB NULL, -- Metadatos por defecto para notas creadas con esta plantilla
    "created_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    "updated_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT "templates_user_id_name_key" UNIQUE ("user_id", "name")
);

COMMENT ON TABLE "templates" IS 'Almacena plantillas definidas por el usuario para la creación de notas.';
COMMENT ON COLUMN "templates"."content_structure" IS 'Estructura de contenido de la plantilla en JSONB, puede incluir placeholders.';
COMMENT ON COLUMN "templates"."default_note_type" IS 'Tipo de nota por defecto que se asignará al usar esta plantilla.';
COMMENT ON COLUMN "templates"."default_metadata" IS 'Metadatos JSONB por defecto para notas creadas con esta plantilla.';


-- Trigger para updated_at en templates
CREATE OR REPLACE TRIGGER set_timestamp_templates
BEFORE UPDATE ON "templates"
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();
*/

-- -----------------------------------------------------------------------------
-- Tabla: project_templates (Tabla de Unión Many-to-Many)
-- Asocia plantillas específicas a proyectos.
-- -----------------------------------------------------------------------------
/*
CREATE TABLE IF NOT EXISTS "project_templates" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "project_id" UUID NOT NULL REFERENCES "projects"("id") ON DELETE CASCADE,
    "template_id" UUID NOT NULL REFERENCES "templates"("id") ON DELETE CASCADE,
    "user_id" TEXT NOT NULL REFERENCES "user_profiles"("user_id") ON DELETE CASCADE, -- Para asegurar que la asociación es del mismo usuario
    "sort_order" INTEGER DEFAULT 0 NULL,
    "created_at" TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT "project_templates_project_id_template_id_key" UNIQUE ("project_id", "template_id")
);

COMMENT ON TABLE "project_templates" IS 'Asocia plantillas específicas a proyectos.';
COMMENT ON COLUMN "project_templates"."sort_order" IS 'Para ordenar las plantillas disponibles para un proyecto específico.';
COMMENT ON COLUMN "project_templates"."user_id" IS 'Usuario propietario de la asociación, debe coincidir con el del proyecto y la plantilla.';
*/

-- #############################################################################
-- # 4. ÍNDICES
-- # Crear índices para optimizar las consultas.
-- #############################################################################

-- Índices para user_profiles
CREATE INDEX IF NOT EXISTS "idx_user_profiles_email" ON "user_profiles"("email");

-- Índices para projects
CREATE INDEX IF NOT EXISTS "idx_projects_user_id" ON "projects"("user_id");
CREATE INDEX IF NOT EXISTS "idx_projects_name" ON "projects"("name"); -- Para búsquedas por nombre de proyecto
CREATE INDEX IF NOT EXISTS "idx_projects_parent_project_id" ON "projects"("parent_project_id");

-- Índices para sources
CREATE INDEX IF NOT EXISTS "idx_sources_user_id" ON "sources"("user_id");
CREATE INDEX IF NOT EXISTS "idx_sources_type" ON "sources"("type");
CREATE INDEX IF NOT EXISTS "idx_sources_url" ON "sources"("url");
CREATE INDEX IF NOT EXISTS "idx_sources_title" ON "sources"("title");

-- Índices para notes
CREATE INDEX IF NOT EXISTS "idx_notes_user_id" ON "notes"("user_id");
CREATE INDEX IF NOT EXISTS "idx_notes_project_id" ON "notes"("project_id");
CREATE INDEX IF NOT EXISTS "idx_notes_source_id" ON "notes"("source_id");
CREATE INDEX IF NOT EXISTS "idx_notes_title" ON "notes"("title"); -- Para búsquedas por título
CREATE INDEX IF NOT EXISTS "idx_notes_type" ON "notes"("type");
CREATE INDEX IF NOT EXISTS "idx_notes_created_at" ON "notes"("created_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_notes_updated_at" ON "notes"("updated_at" DESC);
-- CREATE INDEX IF NOT EXISTS idx_notes_embedding ON notes USING hnsw (embedding vector_l2_ops); -- Ejemplo para pgvector (HNSW)
-- CREATE INDEX IF NOT EXISTS idx_notes_embedding_cosine ON notes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100); -- Ejemplo para pgvector (IVFFlat)
-- Los índices de embedding se añadirán cuando se implemente la funcionalidad.

-- Índices para keywords
CREATE INDEX IF NOT EXISTS "idx_keywords_user_id_name" ON "keywords"("user_id", "name"); -- Ya cubierto por UNIQUE constraint, pero explícito
CREATE INDEX IF NOT EXISTS "idx_keywords_name" ON "keywords"("name"); -- Si se busca keywords sin filtrar por usuario

-- Índices para note_keywords
-- La PK compuesta (note_id, keyword_id) ya crea un índice.
-- Índices adicionales pueden ser útiles para consultas específicas:
CREATE INDEX IF NOT EXISTS "idx_note_keywords_note_id" ON "note_keywords"("note_id");
CREATE INDEX IF NOT EXISTS "idx_note_keywords_keyword_id" ON "note_keywords"("keyword_id");

-- Índices para note_links
CREATE INDEX IF NOT EXISTS "idx_note_links_user_id" ON "note_links"("user_id");
CREATE INDEX IF NOT EXISTS "idx_note_links_source_note_id" ON "note_links"("source_note_id");
CREATE INDEX IF NOT EXISTS "idx_note_links_target_note_id" ON "note_links"("target_note_id");
CREATE INDEX IF NOT EXISTS "idx_note_links_link_type" ON "note_links"("link_type");

-- Índices para templates
/*
CREATE INDEX IF NOT EXISTS "idx_templates_user_id" ON "templates"("user_id");
CREATE INDEX IF NOT EXISTS "idx_templates_name" ON "templates"("name");
*/

-- Índices para project_templates
/*
CREATE INDEX IF NOT EXISTS "idx_project_templates_user_id" ON "project_templates"("user_id");
CREATE INDEX IF NOT EXISTS "idx_project_templates_project_id" ON "project_templates"("project_id");
CREATE INDEX IF NOT EXISTS "idx_project_templates_template_id" ON "project_templates"("template_id");
*/


-- #############################################################################
-- # FIN DEL ESQUEMA
-- #############################################################################
