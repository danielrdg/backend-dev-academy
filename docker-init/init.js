// Seleciona (ou cria) o banco
db = db.getSiblingDB("roteamento_ia");

// --- prompts ---
if (!db.getCollectionNames().includes("prompts")) {
  db.createCollection("prompts");
}
// índice para buscar por modelo de IA
db.prompts.createIndex({ ia_model: 1 });

// --- executions ---
if (!db.getCollectionNames().includes("executions")) {
  db.createCollection("executions");
}
// índices para métricas
db.executions.createIndex({ prompt_id: 1 });
db.executions.createIndex({ timestamp: 1 });
