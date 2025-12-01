pipeline {
  // ใช้ Kubernetes Agent เพื่อสร้าง Container ที่มี Python (สำหรับลง sqlfluff และ mysql-client)
  agent {
    kubernetes {
      yaml '''
      apiVersion: v1
      kind: Pod
      spec:
        containers:
        - name: db-tools
          image: python:3.9-bullseye
          command: ['cat']
          tty: true
      '''
    }
  }

  // สร้างช่องกรอกข้อมูลให้เหมือนของจริง
  parameters {
    string(name: 'DATABASE', defaultValue: 'crm', description: 'Folder Level 1')
    string(name: 'SP_DATE', defaultValue: '202312', description: 'Folder Level 2 (YearMonth)')
    string(name: 'SCHEMA', defaultValue: 'schema_v1', description: 'Folder Level 3')
    string(name: 'SQL_FILE', defaultValue: 'init.sql', description: 'SQL Filename')
    string(name: 'TAG_VERSION', defaultValue: 'main', description: 'Branch to build')
  }

  environment {
    // Config เชื่อมต่อ Database จำลอง (mysql-lab)
    DB_HOST = 'mysql-lab'
    DB_USER = 'root'
    DB_PASS = 'root'
    
    // ตั้งค่า Git ของคุณ
    GIT_REPO = 'https://github.com/KoniPN/devops-lab-project.git'
    GIT_CREDENTIAL_ID = 'github-login'
  }
  
  stages {
    stage('Install Tools') {
      steps {
        container('db-tools') {
            // ติดตั้ง Tools หน้างาน (เพราะ Image Python มันโล่งๆ)
            sh """
                echo "⏳ Installing SQL Fluff & MySQL Client..."
                pip install sqlfluff
                apt-get update && apt-get install -y default-mysql-client
                
                echo "✅ Tools Ready:"
                sqlfluff --version
                mysql --version
            """
        }
      }
    }

    stage('Checkout Code') {
      steps {
        // ดึงโค้ดจาก Git (ใช้ branch ตามที่กรอกมา)
        git branch: params.TAG_VERSION, url: GIT_REPO, credentialsId: GIT_CREDENTIAL_ID
      }
    }

    stage('SQL Syntax Check') {
      steps {
       container('db-tools') {
          script {
            // ประกอบร่าง Path ตามโครงสร้างโฟลเดอร์
            def scriptPath = "${params.DATABASE}/${params.SP_DATE}/${params.SCHEMA}/${params.SQL_FILE}"
            
            echo "🔍 Checking syntax for: ${scriptPath}"
            
            // สั่ง Lint SQL (ใช้ dialect mysql)
            // --dialect mysql สำคัญมาก ไม่งั้น sqlfluff จะงง syntax
            sh "sqlfluff lint ${scriptPath} --dialect mysql"
          }
        }
      }
    }

    stage('Run SQL on DB') {
      steps {
        container('db-tools') {
            script {
              def scriptPath = "${params.DATABASE}/${params.SP_DATE}/${params.SCHEMA}/${params.SQL_FILE}"
              
              echo "🚀 Executing SQL on Host: ${DB_HOST}..."
              
              // รันคำสั่ง mysql ยิงไปที่ Database
              def result = sh(
                script: """
                  mysql -h ${DB_HOST} -P 3306 -u ${DB_USER} --password=${DB_PASS} -D mydb < ${scriptPath}
                """,
                returnStatus: true
              )
                
              if (result == 0) {
                echo "[✅] SQL executed successfully"
                // แถม: ลอง Select มาโชว์
                sh "mysql -h ${DB_HOST} -u ${DB_USER} --password=${DB_PASS} -D mydb -e 'SHOW TABLES; SELECT * FROM users_test;'"
              } else {
                error "[❌] SQL execution failed with exit code ${result}"
              }
            }
        }
      }
    }
  }
  
  post {
      always {
          cleanWs()
      }
  }
}