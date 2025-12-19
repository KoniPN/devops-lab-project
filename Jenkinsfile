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
                    while (!isPassed) {
                        echo "--- 🕵️‍♂️ เริ่มสแกนหา Secret... ---"
                        
                        // สแกนและเก็บค่า exit code
                        def exitCode = sh(
                            script: "docker run --rm -v ${WORKSPACE}:/src aquasec/trivy fs --scanners secret --exit-code 1 /src",
                            returnStatus: true
                        )

                        echo "DEBUG: Trivy Exit Code = ${exitCode}"

                        if (exitCode == 0) {
                            echo "✅ Scan ผ่าน! ไม่เจอ Secret"
                            isPassed = true
                        } else {
                            echo "❌ Scan ไม่ผ่าน! เจอ Secret Key"
                            
                            // --- จุดที่ 1: สร้างปุ่มกด ---
                            // Input จะทำให้ Pipeline หยุดรอ (Paused)
                            // ให้สังเกตใน Console Output จะมี Link ให้กด "Proceed" หรือ "Abort"
                            try {
                                input message: '🚨 เจอ Secret Key! กรุณาลบไฟล์ใน Git แล้วกดปุ่มนี้เพื่อตรวจใหม่', 
                                      ok: '✅ แก้แล้ว! ตรวจใหม่',
                                      submitterParameter: 'approve'
                                
                                // --- จุดที่ 2: บังคับดึง Code ล่าสุด ---
                                echo "🔄 กำลังดึง Code ล่าสุด..."
                                withCredentials([usernamePassword(credentialsId: GIT_CREDS_ID, passwordVariable: 'GIT_PASS', usernameVariable: 'GIT_USER')]) {
                                    sh """
                                        git config user.email "jenkins@example.com"
                                        git config user.name "Jenkins Bot"
                                        # บังคับดึง Branch main ล่าสุด
                                        git pull https://${GIT_USER}:${GIT_PASS}@github.com/KoniPN/devops-lab-project.git main
                                    """
                                }
                                
                            } catch (err) {
                                echo "User aborted the build"
                                error("❌ User ยกเลิกการตรวจสอบ")
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