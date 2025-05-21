
DB_USER="seu_usuario"
DB_PASSWORD="sua_senha"
DB_NAME="seice_estagiarios"
BACKUP_DIR="/caminho/para/backups"


mkdir -p $BACKUP_DIR


BACKUP_FILE="$BACKUP_DIR/$DB_NAME-$(date +%Y%m%d-%H%M%S).sql"

# Executar o backup
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_FILE


gzip $BACKUP_FILE

echo "Backup concluído: $BACKUP_FILE.gz"

# Remover backups antigos (manter apenas os últimos 7 dias)
find $BACKUP_DIR -name "$DB_NAME-*.sql.gz" -type f -mtime +7 -delete