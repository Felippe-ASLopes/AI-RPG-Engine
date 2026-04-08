-- ==========================================
-- SCRIPT DE CRIAÇÃO: FELPINHO's RPG ENGINE
-- BANCO DE DADOS: SQLite
-- ==========================================

PRAGMA foreign_keys = ON;

-- ==========================================
-- ESTRUTURA DE SETUP (PRESET)
-- ==========================================

CREATE TABLE IF NOT EXISTS CAMPAIGN_setup (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    theme TEXT, -- JSON Array
    tone TEXT, -- JSON Array
    world_rules TEXT -- JSON Array
);

CREATE TABLE IF NOT EXISTS CONFIGS_setup (
    id TEXT PRIMARY KEY,
    campaign_base_id TEXT,
    allow_nsfw BOOLEAN DEFAULT 0,
    allow_gore BOOLEAN DEFAULT 0,
    banned_themes TEXT, -- JSON Array
    difficulty TEXT,
    FOREIGN KEY (campaign_base_id) REFERENCES CAMPAIGN_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS EVENTS_setup (
    id TEXT PRIMARY KEY,
    campaign_base_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    trigger TEXT,
    outcomes TEXT, -- JSON Array
    status TEXT, -- "Inactive | Started"
    FOREIGN KEY (campaign_base_id) REFERENCES CAMPAIGN_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS QUESTS_setup (
    title TEXT PRIMARY KEY,
    campaign_base_id TEXT,
    description TEXT,
    trigger TEXT, -- JSON Array
    completion TEXT, -- JSON Array
    is_mandatory BOOLEAN,
    was_completed BOOLEAN DEFAULT 0,
    FOREIGN KEY (campaign_base_id) REFERENCES CAMPAIGN_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CHARACTERS_setup (
    id TEXT PRIMARY KEY,
    campaign_base_id TEXT,
    name TEXT NOT NULL,
    description TEXT, -- JSON Array
    identity TEXT, -- JSON Array
    personality TEXT, -- JSON Array
    backstory TEXT,
    weaknesses TEXT, -- JSON Array
    mood TEXT, -- JSON Array
    FOREIGN KEY (campaign_base_id) REFERENCES CAMPAIGN_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ITENS_setup (
    id TEXT PRIMARY KEY,
    campaign_base_id TEXT,
    name TEXT NOT NULL,
    description TEXT, -- JSON Array
    type TEXT,
    rarity TEXT,
    FOREIGN KEY (campaign_base_id) REFERENCES CAMPAIGN_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS LOCATIONS_setup (
    id TEXT PRIMARY KEY,
    campaign_base_id TEXT,
    name TEXT NOT NULL,
    type TEXT,
    description TEXT, -- JSON Array
    status TEXT, -- JSON Object
    FOREIGN KEY (campaign_base_id) REFERENCES CAMPAIGN_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS STATUS_setup (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    hp INTEGER,
    mana INTEGER,
    stamina INTEGER,
    injuries TEXT, -- JSON Array
    active_effects TEXT, -- JSON Array
    FOREIGN KEY (character_id) REFERENCES CHARACTERS_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS EQUIPMENT_setup (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    weapon_id TEXT,
    shield_id TEXT,
    head_id TEXT,
    body_id TEXT,
    legs_id TEXT,
    feet_id TEXT,
    hands_id TEXT,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS_setup(id) ON DELETE CASCADE,
    FOREIGN KEY (weapon_id) REFERENCES ITENS_setup(id) ON DELETE SET NULL,
    FOREIGN KEY (shield_id) REFERENCES ITENS_setup(id) ON DELETE SET NULL,
    FOREIGN KEY (head_id) REFERENCES ITENS_setup(id) ON DELETE SET NULL,
    FOREIGN KEY (body_id) REFERENCES ITENS_setup(id) ON DELETE SET NULL,
    FOREIGN KEY (legs_id) REFERENCES ITENS_setup(id) ON DELETE SET NULL,
    FOREIGN KEY (feet_id) REFERENCES ITENS_setup(id) ON DELETE SET NULL,
    FOREIGN KEY (hands_id) REFERENCES ITENS_setup(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS SKILLS_setup (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    name TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS RELATIONSHIPS_setup (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    character_target_id TEXT,
    name TEXT,
    affinity_level TEXT,
    can_companion BOOLEAN DEFAULT 0,
    can_romance BOOLEAN DEFAULT 0,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS_setup(id) ON DELETE CASCADE,
    FOREIGN KEY (character_target_id) REFERENCES CHARACTERS_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS INVENTORIES_setup (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    item_id TEXT,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS_setup(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES ITENS_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS C_APPEARANCES_setup (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    face TEXT, -- JSON Array
    hair TEXT, -- JSON Array
    body TEXT, -- JSON Array
    outfit TEXT, -- JSON Array
    current_state TEXT, -- JSON Array
    FOREIGN KEY (character_id) REFERENCES CHARACTERS_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS E_APPEARANCES_setup (
    id TEXT PRIMARY KEY,
    entity_id TEXT, -- Polimórfico (pode referenciar ITENS ou LOCATIONS)
    characteristics TEXT, -- JSON Array
    current_state TEXT -- JSON Array
);

CREATE TABLE IF NOT EXISTS METADATA_setup (
    id TEXT PRIMARY KEY,
    id_appearance TEXT,
    lora_ref TEXT,
    img_path TEXT,
    img_alt_path TEXT,
    FOREIGN KEY (id_appearance) REFERENCES C_APPEARANCES_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS EFFECTS_setup (
    id TEXT PRIMARY KEY,
    item_id TEXT,
    category TEXT,
    type TEXT,
    value TEXT,
    duration TEXT,
    FOREIGN KEY (item_id) REFERENCES ITENS_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ATMOSPHERES_setup (
    id TEXT PRIMARY KEY,
    location_id TEXT,
    mood TEXT, -- JSON Array
    lighting TEXT, -- JSON Array
    sounds TEXT, -- JSON Array
    FOREIGN KEY (location_id) REFERENCES LOCATIONS_setup(id) ON DELETE CASCADE
);


-- ==========================================
-- ESTRUTURA DE RUNTIME (WORLD STATE)
-- ==========================================

CREATE TABLE IF NOT EXISTS CAMPAIGN_STATE (
    id TEXT PRIMARY KEY,
    campaign_base_id TEXT,
    title TEXT NOT NULL,
    theme TEXT, -- JSON Array
    tone TEXT, -- JSON Array
    weather TEXT,
    time_of_day TEXT,
    world_rules TEXT, -- JSON Array
    FOREIGN KEY (campaign_base_id) REFERENCES CAMPAIGN_setup(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS LAST_ROUNDS (
    round_number INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id TEXT,
    narrative TEXT,
    player_actions TEXT, -- JSON Array
    FOREIGN KEY (campaign_id) REFERENCES CAMPAIGN_STATE(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS EVENTS (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    trigger TEXT,
    outcomes TEXT, -- JSON Array
    status TEXT, -- "Inactive | Started | Completed"
    FOREIGN KEY (campaign_id) REFERENCES CAMPAIGN_STATE(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CHARACTERS (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    name TEXT NOT NULL,
    description TEXT, -- JSON Array
    identity TEXT, -- JSON Array
    personality TEXT, -- JSON Array
    backstory TEXT,
    weaknesses TEXT, -- JSON Array
    mood TEXT, -- JSON Array
    FOREIGN KEY (campaign_id) REFERENCES CAMPAIGN_STATE(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ACTIVE_CHARACTERS (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    character_id TEXT,
    role_type TEXT, -- "Player | Companion | Enemy | NPC"
    turn_order INTEGER,
    FOREIGN KEY (campaign_id) REFERENCES CAMPAIGN_STATE(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ITENS (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    name TEXT NOT NULL,
    description TEXT, -- JSON Array
    type TEXT,
    rarity TEXT,
    FOREIGN KEY (campaign_id) REFERENCES CAMPAIGN_STATE(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS LOCATIONS (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    name TEXT NOT NULL,
    type TEXT,
    description TEXT, -- JSON Array
    status TEXT, -- JSON Object
    FOREIGN KEY (campaign_id) REFERENCES CAMPAIGN_STATE(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS INVENTORIES (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    item_id TEXT,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES ITENS(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS STATUS (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    hp INTEGER,
    mana INTEGER,
    stamina INTEGER,
    injuries TEXT, -- JSON Array
    active_effects TEXT, -- JSON Array
    FOREIGN KEY (character_id) REFERENCES CHARACTERS(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS EQUIPMENT (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    weapon_id TEXT,
    shield_id TEXT,
    head_id TEXT,
    body_id TEXT,
    legs_id TEXT,
    feet_id TEXT,
    hands_id TEXT,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS(id) ON DELETE CASCADE,
    FOREIGN KEY (weapon_id) REFERENCES ITENS(id) ON DELETE SET NULL,
    FOREIGN KEY (shield_id) REFERENCES ITENS(id) ON DELETE SET NULL,
    FOREIGN KEY (head_id) REFERENCES ITENS(id) ON DELETE SET NULL,
    FOREIGN KEY (body_id) REFERENCES ITENS(id) ON DELETE SET NULL,
    FOREIGN KEY (legs_id) REFERENCES ITENS(id) ON DELETE SET NULL,
    FOREIGN KEY (feet_id) REFERENCES ITENS(id) ON DELETE SET NULL,
    FOREIGN KEY (hands_id) REFERENCES ITENS(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS SKILLS (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    name TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS RELATIONSHIPS (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    character_target_id TEXT,
    name TEXT,
    affinity_level TEXT,
    can_companion BOOLEAN DEFAULT 0,
    can_romance BOOLEAN DEFAULT 0,
    FOREIGN KEY (character_id) REFERENCES CHARACTERS(id) ON DELETE CASCADE,
    FOREIGN KEY (character_target_id) REFERENCES CHARACTERS(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ATMOSPHERES (
    id TEXT PRIMARY KEY,
    location_id TEXT,
    mood TEXT, -- JSON Array
    lighting TEXT, -- JSON Array
    sounds TEXT, -- JSON Array
    FOREIGN KEY (location_id) REFERENCES LOCATIONS(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS EFFECTS (
    id TEXT PRIMARY KEY,
    item_id TEXT,
    category TEXT,
    type TEXT,
    value TEXT,
    duration TEXT,
    FOREIGN KEY (item_id) REFERENCES ITENS(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS C_APPEARANCES (
    id TEXT PRIMARY KEY,
    character_id TEXT,
    face TEXT, -- JSON Array
    hair TEXT, -- JSON Array
    body TEXT, -- JSON Array
    outfit TEXT, -- JSON Array
    current_state TEXT, -- JSON Array
    FOREIGN KEY (character_id) REFERENCES CHARACTERS(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS E_APPEARANCES (
    id TEXT PRIMARY KEY,
    entity_id TEXT, -- Polimórfico (pode referenciar ITENS ou LOCATIONS)
    characteristics TEXT, -- JSON Array
    current_state TEXT -- JSON Array
);

CREATE TABLE IF NOT EXISTS METADATA (
    id TEXT PRIMARY KEY,
    entity_id TEXT, -- Polimórfico
    lora_ref TEXT,
    img_path TEXT,
    img_alt_path TEXT
);