# 🚀 Guía de Despliegue en Alibaba Cloud - SolucionaEnfermedades

## 🔑 Información de Instancia ECS

**Instance ID:** `501018520840052`

## 📋 Requisitos Previos

### 1. Instalar Alibaba Cloud CLI
```bash
# Instalar en Windows (PowerShell)
Invoke-WebRequest -Uri https://github.com/aliyun/aliyun-cli/releases/download/v3.0.135/aliyun-cli-windows-3.0.135-amd64.zip -OutFile aliyun-cli.zip
Expand-Archive -Path aliyun-cli.zip -DestinationPath $HOME\aliyun-cli
Add-Content -Path $PROFILE -Value "`nfunction aliyun { & `$HOME\aliyun-cli\aliyun` $args }"

# Instalar en macOS/Linux
curl -o aliyun-cli-linux-latest-amd64.tgz https://aliyun-cli.oss-cn-hangzhou.aliyuncs.com/aliyun-cli-linux-latest-amd64.tgz
tar -xzvf aliyun-cli-linux-latest-amd64.tgz
sudo mv aliyun /usr/local/bin/
```

### 2. Configurar Credenciales
```bash
aliyun configure
# Ingresar AccessKey ID y AccessKey Secret de Alibaba Cloud
```

## 🚀 Comandos de Despliegue

### 1. Iniciar Instancia ECS
```bash
aliyun ecs StartInstance --InstanceId 501018520840052
```

### 2. Verificar Estado de la Instancia
```bash
aliyun ecs DescribeInstances --InstanceId 501018520840052 --output cols=Status,InstanceName,PublicIpAddress
```

### 3. Conectarse a la Instancia (SSH)
```bash
# Reemplazar <PUBLIC_IP> con la IP de tu instancia
ssh root@<PUBLIC_IP>
```

### 4. Desplegar la Aplicación
```bash
# En la instancia remota:
git clone https://github.com/AngelTroncoso/solucionaenfermedades.git
cd solucionaenfermedades

# Configurar backend
cp backend/.env.example backend/.env
# Editar backend/.env con las claves reales

# Instalar dependencias backend
pip install -r backend/requirements.txt

# Instalar dependencias frontend
cd frontend
npm install
npm run build

# Ejecutar aplicación
cd ..
python backend/main.py --dashboard
```

## 🔧 Métodos Alternativos de Despliegue

### Opción A: Usando Alibaba Cloud Console (Web)
1. Ingresar a [Alibaba Cloud Console](https://console.alibabacloud.com/)
2. Navegar a ECS (Elastic Compute Service)
3. Seleccionar instancia `501018520840052`
4. Hacer clic en "Start" para iniciar
5. Usar "Connect" para acceder via SSH o VNC

### Opción B: Usando Docker (Recomendado)
```bash
# Crear Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

# Instalar dependencias backend
RUN pip install -r backend/requirements.txt

# Instalar Node.js para frontend
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Build frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Ejecutar aplicación
WORKDIR /app
CMD ["python", "backend/main.py", "--dashboard"]

# Construir y ejecutar
docker build -t solucionaenfermedades .
docker run -p 80:80 solucionaenfermedades
```

### Opción C: Usando Serverless (Función Computación)
```bash
# Instalar Serverless Framework
npm install -g serverless

# Configurar serverless.yml
service: solucionaenfermedades
provider:
  name: aliyun
  runtime: python3
  region: cn-hangzhou

functions:
  api:
    handler: backend/main.handler
    events:
      - http:
          path: /api
          method: get

# Desplegar
serverless deploy
```

## 📊 Monitoreo y Mantenimiento

### 1. Verificar Métricas
```bash
aliyun cms DescribeMetricList --MetricName CPUUtilization --Namespace acs_ecs_dashboard --Dimensions '[{"InstanceId":"501018520840052"}]'
```

### 2. Configurar Alertas
```bash
aliyun cms PutContact --ContactName "Admin" --Phone "1234567890" --Email "admin@example.com"
aliyun cms CreateAlarm --AlarmName "HighCPU" --MetricName CPUUtilization --Threshold 80 --ComparisonOperator GreaterThanThreshold
```

### 3. Backup Automático
```bash
aliyun ecs CreateSnapshot --InstanceId 501018520840052 --DiskId <DISK_ID> --SnapshotName "Backup-$(date +%Y%m%d)"
```

## 🔐 Configuración de Seguridad

### 1. Configurar Security Group
```bash
aliyun ecs AuthorizeSecurityGroup --SecurityGroupId <SG_ID> --IpProtocol tcp --PortRange 80/80 --SourceCidrIp 0.0.0.0/0
aliyun ecs AuthorizeSecurityGroup --SecurityGroupId <SG_ID> --IpProtocol tcp --PortRange 443/443 --SourceCidrIp 0.0.0.0/0
```

### 2. Configurar SSL
```bash
aliyun ssl CreateCertificate --CertName "solucionaenfermedades" --CertType 1 --DomainName "tudominio.com"
```

## 📚 Recursos Adicionales

- [Documentación Alibaba Cloud CLI](https://www.alibabacloud.com/help/doc-detail/120107.htm)
- [Guía de ECS](https://www.alibabacloud.com/product/ecs)
- [Serverless en Alibaba Cloud](https://www.alibabacloud.com/product/function-compute)

## ⚠️ Notas Importantes

1. **Nunca expongas las claves de API** - Mantén `backend/.env` seguro
2. **Configura HTTPS** - Usa certificados SSL para producción
3. **Monitorea recursos** - Configura alertas para CPU/memoria
4. **Haz backups regulares** - Usa snapshots de ECS

**🎉 ¡Listo para desplegar en Alibaba Cloud con Instance ID: 501018520840052!**