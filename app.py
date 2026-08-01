# ---------------------------------------------------------
# 比對答案與計分 (總分 20 分)
# ---------------------------------------------------------
if submit_button:
    if not name or not dept:
        st.warning("請先填寫姓名與組別！")
    else:
        score = 0
        total_items = 20  # 固定總分為 20 分
        
        for q in questions:
            user_ans = user_answers[q["id"]]
            correct_ans = q["answer"]
            
            # 單選題：答對得 1 分
            if q["type"] == "single":
                if [user_ans] == correct_ans:
                    score += 1
                    
            # 多選題：選對 1 個正確選項得 1 分 (最高 2 分，選錯不扣分)
            elif q["type"] == "multiple":
                for option in user_ans:
                    if option in correct_ans:
                        score += 1
                        
            # 第 3 題（質量目標 6 個子項）：每對 1 項得 1 分 (最高 6 分)
            elif q["type"] == "group_single":
                for sub_q in q["sub_questions"]:
                    user_sub_ans = user_ans[sub_q["sub_id"]]
                    if user_sub_ans == sub_q["answer"]:
                        score += 1

        pass_rate = (score / total_items) * 100
        is_pass = score >= 16  # 達到 16 分即為合格 (80%)
        
        st.success(f"提交成功！得分：{score} / {total_items}（合格率：{pass_rate:.1f}%）")
        if is_pass:
            st.balloons()
            st.success("🎉 恭喜通過入職培訓考核！")
        else:
            st.error("⚠️ 未達 16 分 (80%) 合格標準。")
