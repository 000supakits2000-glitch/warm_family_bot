import json
import os
from datetime import datetime
from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY", "ใส่_API_KEY_ของคุณที่นี่")
client = genai.Client(api_key=API_KEY)

HISTORY_FILE = "history.json"
OUTPUT_FILE = "today_episode.txt"


def load_history():
  if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return []


def save_history(history):
  # เก็บประวัติล่าสุด 30 ตอน เพื่อไม่ให้ Prompt ยาวเกินไป
  with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(history[-30:], f, ensure_ascii=False, indent=2)


def generate_daily_episode(history):
  past_summary = (
      "\n".join([
          f"- ตอน: {item['title']} | ตัวละครเดิม: {item['characters_summary']}"
          for item in history
      ])
      if history
      else "ยังไม่มีประวัติตอนเก่า"
  )

  prompt = f"""
คุณคือนักเขียนบทและผู้กำกับซีรีส์สั้นแนวตั้ง (9:16) แนวฮีลใจสไตล์ไทย เรื่อง "ครอบครัวอบอุ่น"

ประวัติตอนและตัวละครที่เคยสร้างไปแล้ว (ห้ามออกแบบตัวละคร ซ้ำหน้าตา ชุด สีผม อาชีพ หรือพล็อตเรื่องเดิม):
{past_summary}

ภารกิจของคุณคือสร้างบทละครสั้น 1 ตอน (5 ฉาก ขนาด 9:16) พร้อมข้อคิดสอนใจ โดยตอบกลับเป็น JSON ตามโครงสร้างนี้เท่านั้น:
{{
  "episode_title": "ชื่อตอนสั้นๆ น่าสนใจ",
  "characters": [
    {{
      "name": "ชื่อตัวละคร (ภาษาไทย)",
      "role": "ความสัมพันธ์/บทบาท เช่น พ่อวัย 55, ลูกสาววัย 24",
      "personality": "บุคลิก นิสัย",
      "appearance_thai": "ระบุหน้าตา รูปร่าง สีผม ทรงผม เครื่องแต่งกาย สีเสื้อผ้าให้ชัดเจน",
      "character_prompt_en": "English character design prompt specifying exact age, Thai ethnicity, face features, exact hair color & hairstyle, exact outfit & colors, personality vibe, studio lighting, consistent character sheet, vertical 9:16 aspect ratio"
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "scene_purpose": "เปิดเรื่อง/ปูบรรยากาศ",
      "camera_and_action_thai": "อธิบายมุมกล้อง (เช่น Close-up, Medium shot) และการกระทำของตัวละครอย่างละเอียด",
      "dialogue_thai": "บทสนทนาหรือเสียงพากย์ภาษาไทยที่เป็นธรรมชาติ",
      "visual_prompt_en": "Detailed English image/video prompt describing the exact scene, camera angle, action, warm Thai home lighting, and MUST repeat the exact hair color, hairstyle, and outfit of the characters from character_prompt_en so their appearance stays 100% consistent, cinematic realistic style, vertical 9:16 aspect ratio"
    }}
  ],
  "moral_of_the_story": "ข้อคิดสอนใจสั้นๆ กินใจ 1-2 บรรทัด สำหรับขึ้นข้อความปิดท้ายคลิป",
  "caption_and_hashtags": "แคปชันพร้อมแฮชแท็กสำหรับโพสต์โซเชียล"
}}

เงื่อนไขบังคับ:
1. ต้องมีตัวละครหลัก 2-3 คน ที่ออกแบบใหม่ไม่ซ้ำกับประวัติเดิม
2. ต้องมีครบ 5 ฉากพอดี (scene_number 1 ถึง 5):
   - ฉาก 1: เปิดเรื่อง/ปูบรรยากาศ
   - ฉาก 2: ปมเล็กๆ หรือความรู้สึกในใจ
   - ฉาก 3: จุดเปลี่ยน/การกระทำหรือคำพูดที่แสดงความห่วงใย
   - ฉาก 4: จุดพีคฮีลใจ/คลี่คลายอารมณ์
   - ฉาก 5: บทสรุปอบอุ่น พร้อมสอดแทรกข้อคิดสอนใจในบทพูดอย่างเป็นธรรมชาติ
3. ใน visual_prompt_en ของทุกฉาก ต้องระบุลักษณะตัวละคร (สีผม ทรงผม เสื้อผ้า) ให้ตรงกับ character_prompt_en ทุกประการ และต้องมีคำว่า "vertical 9:16 aspect ratio" ทุกฉาก
"""

  response = client.models.generate_content(
      model="gemini-3.8-flash",
      contents=prompt,
      config=types.GenerateContentConfig(response_mime_type="application/json"),
  )

  return json.loads(response.text)


def format_and_save_txt(data):
  today = datetime.now().strftime("%Y-%m-%d")
  lines = [
      f"=== ซีรีส์สั้นฮีลใจ 'ครอบครัวอบอุ่น' ประจำวันที่ {today} ===",
      f"ชื่อตอน: {data['episode_title']}\n",
      "--------------------------------------------------",
      "1. การออกแบบตัวละคร (Character Design - สำหรับคุมหน้าและชุดให้คงเดิม)",
      "--------------------------------------------------",
  ]

  for idx, char in enumerate(data["characters"], 1):
    lines.extend([
        f"ตัวละครที่ {idx}: {char['name']} ({char['role']})",
        f"- บุคลิก: {char['personality']}",
        f"- ลักษณะ/สีผม/ชุด: {char['appearance_thai']}",
        f"- Character Prompt (EN): {char['character_prompt_en']}\n",
    ])

  lines.extend([
      "--------------------------------------------------",
      "2. บทละครและคำสั่งสร้างภาพ/วิดีโอ (5 ฉาก ขนาด 9:16)",
      "--------------------------------------------------",
  ])

  for scene in data["scenes"]:
    lines.extend([
        f"[ฉากที่ {scene['scene_number']}: {scene['scene_purpose']}]",
        f"- มุมกล้อง/แอ็กชัน: {scene['camera_and_action_thai']}",
        f"- บทพูด/เสียงพากย์: {scene['dialogue_thai']}",
        f"- Image/Video Prompt (EN): {scene['visual_prompt_en']}\n",
    ])

  lines.extend([
      "--------------------------------------------------",
      "3. ข้อคิดสอนใจ & แคปชัน",
      "--------------------------------------------------",
      f"ข้อคิดสอนใจ: {data['moral_of_the_story']}\n",
      f"แคปชัน:\n{data['caption_and_hashtags']}",
  ])

  output_text = "\n".join(lines)
  with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(output_text)

  return output_text


if __name__ == "__main__":
  history = load_history()
  print("กำลังสร้างบทละครประจำวัน...")
  episode_data = generate_daily_episode(history)

  # บันทึกไฟล์ข้อความสำหรับนำไปใช้งาน
  result = format_and_save_txt(episode_data)
  print(result)

  # อัปเดตประวัติตัวละครและชื่อตอนลง history.json
  chars_summary = ", ".join([
      f"{c['name']} ({c['role']}, {c['appearance_thai']})"
      for c in episode_data["characters"]
  ])
  history.append({
      "date": datetime.now().strftime("%Y-%m-%d"),
      "title": episode_data["episode_title"],
      "characters_summary": chars_summary,
  })
  save_history(history)
  print(
      f"\nบันทึกเรียบร้อยที่ {OUTPUT_FILE} และอัปเดตประวัติลง {HISTORY_FILE} แล้ว"
  )
