pipeline {
    agent any

    environment {
        IMAGE_NAME = "konipn/devops-lab"
        TAG = "v1-${BUILD_NUMBER}"
        DOCKER_CREDS_ID = "docker-hub-secret"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // --- 1. ตรวจสอบ Secret (แบบวนลูปจนกว่าจะผ่าน) ---
        stage('⛔ Security Check: Secrets') {
            steps {
                script {
                    def isPassed = false
                    
                    // วนลูปจนกว่าค่า isPassed จะเป็น true
                    while (!isPassed) {
                        echo "--- 🕵️‍♂️ Starting Secret Scan... ---"
                        
                        // สั่ง Scan (ใช้ returnStatus: true เพื่อเอาค่า 0 หรือ 1 มาเช็คเอง ไม่ให้ Pipeline พัง)
                        def exitCode = sh(
                            script: "docker run --rm -v ${WORKSPACE}:/src aquasec/trivy fs --scanners secret --exit-code 1 /src",
                            returnStatus: true
                        )

                        if (exitCode == 0) {
                            echo "✅ Scan Passed! No secrets found."
                            isPassed = true // หลุด Loop ไปทำต่อ
                        } else {
                            echo "❌ Scan Failed! Found secrets."
                            
                            // *** จุดมหัศจรรย์อยู่ตรงนี้ ***
                            // Jenkins จะหยุดและสร้างปุ่มให้กด
                            try {
                                input message: '🚨 เจอ Secret Key! ไปลบใน Git เดี๋ยวนี้ แล้วกด Retry เพื่อตรวจใหม่', 
                                      ok: '✅ แก้แล้ว! ตรวจใหม่เลย',
                                      submitter: 'admin' // (Optional) ระบุว่าต้องเป็น admin เท่านั้นที่กดได้
                                
                                // พอกดปุ่ม มันจะไปดึง Code ล่าสุดที่เราเพิ่งแก้มา
                                echo "🔄 Pulling latest code changes..."
                                checkout scm
                                
                            } catch (err) {
                                // ถ้ากด Abort หรือ Cancel
                                error("❌ User aborted the pipeline.")
                            }
                        }
                    }
                }
            }
        }

        stage('Build Image') {
            steps {
                sh "docker build --platform linux/amd64 -t ${IMAGE_NAME}:${TAG} ."
            }
        }

        // --- 2. ตรวจสอบ CVE ด้วย Docker Scout (แบบวนลูปเหมือนกัน) ---
        stage('🛡️ Docker Scout Check') {
            steps {
                script {
                    def isPassed = false
                    while (!isPassed) {
                        withCredentials([usernamePassword(credentialsId: DOCKER_CREDS_ID, passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                            sh "echo $PASS | docker login -u $USER --password-stdin"
                            
                            // เช็ค CVE (Critical)
                            def exitCode = sh(
                                script: """
                                    # ต้องติดตั้ง scout หรือใช้ image scout (ในที่นี้สมมติว่าเครื่องมี scout แล้ว)
                                    docker scout cves ${IMAGE_NAME}:${TAG} --exit-code 1 --only-severity critical
                                """,
                                returnStatus: true
                            )

                            if (exitCode == 0) {
                                isPassed = true
                            } else {
                                // ถ้าเจอช่องโหว่ หยุดรอให้แก้ Base Image หรือ Library
                                try {
                                    input message: '🚨 เจอช่องโหว่ Critical! ไปแก้ Dockerfile แล้วกด Retry', 
                                          ok: '✅ แก้แล้ว! ตรวจใหม่'
                                    
                                    echo "🔄 Re-building image with fixes..."
                                    checkout scm
                                    sh "docker build --platform linux/amd64 -t ${IMAGE_NAME}:${TAG} ." // Build ใหม่ก่อนตรวจซ้ำ
                                } catch (err) {
                                    error("❌ User aborted the pipeline.")
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Push Image') {
            steps {
                sh "docker push ${IMAGE_NAME}:${TAG}"
            }
        }
    }
}