pipeline {
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

  parameters {
    string(name: 'DATABASE', defaultValue: 'crm', description: 'Folder Level 1')
    string(name: 'SP_DATE', defaultValue: '202312', description: 'Folder Level 2')
    string(name: 'SCHEMA', defaultValue: 'schema_v1', description: 'Folder Level 3')
    string(name: 'SQL_FILE', defaultValue: 'init.sql', description: 'SQL Filename')
    string(name: 'TAG_VERSION', defaultValue: 'main', description: 'Branch/Tag')
    choice(name: 'ENVIRONMENT', choices: ['local_lab', 'base_prod'], description: 'Select Environment')
  }

  environment {
    DB_USER = ''
    DB_PASS = ''
    DB_HOST = ''
    GIT_REPO = 'https://github.com/KoniPN/devops-lab-project.git'
    GIT_CREDENTIAL_ID = 'github-login'
  }
  
  stages {
    stage('Prepare Tools') {
      steps {
        container('db-tools') {
            sh """
                echo "⏳ Installing Tools..."
                pip install sqlfluff > /dev/null
                apt-get update && apt-get install -y default-mysql-client > /dev/null
            """
        }
      }
    }

    stage('Select DB Config') {
      steps {
        script {
          currentBuild.displayName = "#${BUILD_NUMBER}(${params.TAG_VERSION})"
          currentBuild.description = "${params.DATABASE}/${params.SP_DATE}/${params.SCHEMA}/${params.SQL_FILE}"
          
          def dbConfig = [
            'local_lab': [host: 'mysql-lab', user: 'root', pass: 'root'],
            'base_prod': [host: 'amaze-prod-db...rds.amazonaws.com', user: 'admin', pass: 'secret']
          ]

          def selected = dbConfig[params.ENVIRONMENT]
          if (!selected) error "❌ Environment ${params.ENVIRONMENT} not found!"

          DB_HOST = selected.host
          DB_USER = selected.user
          DB_PASS = selected.pass
        }
      }
    }

    stage('Checkout Code') {
      steps {
        git branch: params.TAG_VERSION, url: GIT_REPO, credentialsId: GIT_CREDENTIAL_ID
        // 💡 เพิ่มคำสั่งนี้เพื่อดูว่ามีไฟล์อะไรบ้าง (ช่วย Debug)
        sh "ls -R"
      }
    }

    stage('SQL syntax checking') {
      steps {
         container('db-tools') {
            script {
              def scriptPath = "${params.DATABASE}/${params.SP_DATE}/${params.SCHEMA}/${params.SQL_FILE}"
              
              // เช็คว่าไฟล์มีจริงไหม ก่อนรัน
              if (fileExists(scriptPath)) {
                  sh "sqlfluff lint ${scriptPath} --dialect mysql"
              } else {
                  // ถ้าหาไม่เจอ ให้ List ไฟล์มาดูเลยว่ามีอะไรบ้าง
                  sh "ls -R"
                  error "❌ File not found: ${scriptPath} (Check your Git folder structure)"
              }
            }
         }
      }
    }

    stage('Run SQL') {
      steps {
        container('db-tools') {
            script {
              def scriptPath = "${params.DATABASE}/${params.SP_DATE}/${params.SCHEMA}/${params.SQL_FILE}"
              def result = sh(
                script: """
                  mysql -h ${DB_HOST} -P 3306 -u ${DB_USER} --password=${DB_PASS} -D mydb < ${scriptPath}
                """,
                returnStatus: true
              )
              if (result == 0) {
                echo "[✅] SQL executed successfully"
              } else {
                error "[❌] SQL execution failed"
              }
            }
        }
      }
    }
  }
  
  // ⚠️ ลบท่อน post { cleanWs() } ออกไปแล้ว เพื่อแก้ Error NoSuchMethod
}