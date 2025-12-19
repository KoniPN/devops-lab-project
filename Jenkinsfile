pipeline {
    agent {
        kubernetes {
            // ประกาศ Pod ที่มี Trivy และ Kaniko
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: kaniko
                image: gcr.io/kaniko-project/executor:debug
                command: ["/busybox/cat"]
                tty: true
                volumeMounts:
                  - name: docker-config
                    mountPath: /kaniko/.docker
              
              - name: trivy
                image: aquasec/trivy:latest
                command: ["/bin/sh", "-c", "sleep 3600"] # สั่งให้ตื่นรอ
                tty: true
                
              volumes:
                - name: docker-config
                  secret:
                    secretName: docker-hub-secret
                    items:
                      - key: .dockerconfigjson
                        path: config.json
            '''
        }
    }
    
    environment {
        IMAGE_NAME = "konipn/devops-lab"
        TAG = "v1-${BUILD_NUMBER}"
        // แก้เป็น Credential ID ของพี่
        GIT_CREDS_ID = "github-login" 
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // --- 1. ระบบตรวจ Secret แบบวนลูป (ใช้ Container Trivy) ---
        stage('⛔ Security Check: Secrets') {
            steps {
                script {
                    def isPassed = false
                    while (!isPassed) {
                        echo "--- 🕵️‍♂️ เริ่มสแกนหา Secret... ---"
                        
                        def exitCode = 0
                        
                        // เรียกใช้ container ชื่อ 'trivy' แทนการใช้ docker run
                        container('trivy') {
                            // สแกนไฟล์ปัจจุบัน (.)
                            exitCode = sh(
                                script: "trivy fs --scanners secret --exit-code 1 .",
                                returnStatus: true
                            )
                        }

                        echo "DEBUG: Trivy Exit Code = ${exitCode}"

                        if (exitCode == 0) {
                            echo "✅ Scan ผ่าน! ไม่เจอ Secret"
                            isPassed = true
                        } else {
                            echo "❌ Scan ไม่ผ่าน! เจอ Secret Key (หรือ Error)"
                            
                            try {
                                // หยุดรอให้กดปุ่ม
                                input message: '🚨 เจอ Secret Key! ลบไฟล์ใน Git แล้วกดปุ่มนี้เพื่อตรวจใหม่', 
                                      ok: '✅ แก้แล้ว! ตรวจใหม่'
                                
                                // ดึง Code ล่าสุด (รันใน container ปกติที่มี git)
                                echo "🔄 กำลังดึง Code ล่าสุด..."
                                withCredentials([usernamePassword(credentialsId: GIT_CREDS_ID, passwordVariable: 'GIT_PASS', usernameVariable: 'GIT_USER')]) {
                                    sh """
                                        git config user.email "jenkins@example.com"
                                        git config user.name "Jenkins Bot"
                                        git pull https://${GIT_USER}:${GIT_PASS}@github.com/KoniPN/devops-lab-project.git main
                                    """
                                }
                                
                            } catch (err) {
                                error("❌ User ยกเลิกการตรวจสอบ")
                            }
                        }
                    }
                }
            }
        }

        // --- 2. Build Image ด้วย Kaniko ---
        stage('Build & Push Image') {
            steps {
                container('kaniko') {
                    echo "--- 🏗 Building Docker Image ---"
                    sh """
                    /kaniko/executor \
                        --context `pwd` \
                        --destination ${IMAGE_NAME}:${TAG} \
                        --customPlatform=linux/amd64
                    """
                }
            }
        }
        
        // --- 3. Scan Image (Optional) ---
        // (ใส่เพิ่มได้ถ้าต้องการ)
    }
}