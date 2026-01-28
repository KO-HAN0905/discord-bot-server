# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
import json
import os
from datetime import datetime

# 과제 추가 모달
class TaskModal(Modal, title="과제 추가"):
    """과제 추가 모달"""
    
    task_type = TextInput(
        label="과제 종류",
        placeholder="일일: daily, 주간: weekly",
        required=True,
        max_length=10
    )
    
    name = TextInput(
        label="과제 이름",
        placeholder="예: 영어공부, 운동, 프로젝트",
        required=True,
        min_length=1,
        max_length=50
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        """모달 제출 처리"""
        try:
            task_type = "daily" if self.task_type.value.lower() in {"일일", "daily"} else "weekly"
            
            task_data = self.cog.load_tasks()
            task_data[task_type][self.name.value] = {
                "progress": 0,
                "completed": False,
                "created": datetime.now().isoformat()
            }
            self.cog.save_tasks(task_data)
            
            type_text = "일일" if task_type == "daily" else "주간"
            embed = discord.Embed(
                title="✅ 과제 추가됨",
                description=f"**{type_text} 과제:** {self.name.value}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 오류",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

# 과제 UI 버튼 뷰
class TaskView(View):
    """과제 관리 UI 버튼"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)  # 5분 타임아웃
        self.cog = cog
    
    @discord.ui.button(label="➕ 과제 추가", style=discord.ButtonStyle.success)
    async def add_task_button(self, interaction: discord.Interaction, button: Button):
        """과제 추가 버튼"""
        modal = TaskModal(self.cog)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 목록 보기", style=discord.ButtonStyle.primary)
    async def list_button(self, interaction: discord.Interaction, button: Button):
        """목록 보기 버튼"""
        task_data = self.cog.load_tasks()
        embed = discord.Embed(title="📋 과제 목록", color=discord.Color.blue())
        
        if task_data["daily"]:
            daily_text = ""
            for name, data in task_data["daily"].items():
                progress_bar = self.cog.create_progress_bar(data["progress"])
                status = "✅" if data["completed"] else "⏳"
                daily_text += f"{status} **{name}**: {progress_bar} {data['progress']}%\n"
            embed.add_field(name="📅 일일 과제", value=daily_text, inline=False)
        
        if task_data["weekly"]:
            weekly_text = ""
            for name, data in task_data["weekly"].items():
                progress_bar = self.cog.create_progress_bar(data["progress"])
                status = "✅" if data["completed"] else "⏳"
                weekly_text += f"{status} **{name}**: {progress_bar} {data['progress']}%\n"
            embed.add_field(name="📆 주간 과제", value=weekly_text, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❌ 삭제/완료", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: Button):
        """삭제/완료 안내"""
        embed = discord.Embed(
            title="과제 관리",
            description="`!과제 완료 <종류> <이름>` - 과제 완료 표시\n"
                       "`!과제 삭제 <종류> <이름>` - 과제 삭제\n"
                       "`!과제 진행도 <종류> <0-100> <이름>` - 진행도 설정",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task_file = "data/tasks.json"
        self.ensure_file()

    def ensure_file(self):
        """파일 생성 및 초기화"""
        os.makedirs(os.path.dirname(self.task_file), exist_ok=True)
        if not os.path.exists(self.task_file):
            self.save_tasks({"daily": {}, "weekly": {}})

    def load_tasks(self):
        """과제 데이터 로드"""
        try:
            with open(self.task_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"daily": {}, "weekly": {}}

    def save_tasks(self, tasks):
        """과제 데이터 저장"""
        with open(self.task_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    @commands.command(name="과제ui", help="과제 UI 표시")
    async def tasks_ui(self, ctx_or_interaction):
        """과제 관리 UI 버튼 표시"""
        embed = discord.Embed(
            title="📋 과제 관리",
            description="아래 버튼을 클릭하여 과제를 관리하세요.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="기능",
            value="➕ **추가** - 새로운 과제 추가\n"
                  "📋 **목록** - 과제 목록 보기\n"
                  "❌ **삭제/완료** - 과제 삭제 또는 완료",
            inline=False
        )
        
        view = TaskView(self)
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)

    @commands.group(name="과제", help="과제 관리")
    async def tasks(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="📋 과제 도움말", color=discord.Color.blue())
            embed.add_field(name="UI 관리", value="`!과제ui` - 버튼식 UI 사용", inline=False)
            embed.add_field(name="일일 추가", value="`!과제 일일추가 <이름>`", inline=False)
            embed.add_field(name="주간 추가", value="`!과제 주간추가 <이름>`", inline=False)
            embed.add_field(name="삭제", value="`!과제 삭제 <종류(일일/주간)> <이름>`", inline=False)
            embed.add_field(name="완료", value="`!과제 완료 <종류(일일/주간)> <이름>`", inline=False)
            embed.add_field(name="목록", value="`!과제 목록 [종류]`", inline=False)
            await ctx.send(embed=embed)

    @tasks.command(name="일일추가", help="일일 과제 추가")
    async def add_daily(self, ctx, *, name: str):
        """일일 과제 추가"""
        try:
            task_data = self.load_tasks()
            task_id = str(len(task_data["daily"]) + 1)
            task_data["daily"][name] = {
                "progress": 0,
                "completed": False,
                "created": datetime.now().isoformat()
            }
            self.save_tasks(task_data)
            
            embed = discord.Embed(
                title="✅ 일일 과제 추가됨",
                description=f"**{name}** - 진행도: 0%",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    @tasks.command(name="주간추가", help="주간 과제 추가")
    async def add_weekly(self, ctx, *, name: str):
        """주간 과제 추가"""
        try:
            task_data = self.load_tasks()
            task_data["weekly"][name] = {
                "progress": 0,
                "completed": False,
                "created": datetime.now().isoformat()
            }
            self.save_tasks(task_data)
            
            embed = discord.Embed(
                title="✅ 주간 과제 추가됨",
                description=f"**{name}** - 진행도: 0%",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    @tasks.command(name="삭제", help="과제 삭제")
    async def delete_task(self, ctx, task_type: str, *, name: str):
        """과제 삭제"""
        try:
            task_type = "daily" if task_type in {"일일", "daily"} else "weekly"
            task_data = self.load_tasks()
            
            if name in task_data[task_type]:
                del task_data[task_type][name]
                self.save_tasks(task_data)
                await ctx.send(f"✅ **{name}** 과제가 삭제되었습니다.")
            else:
                await ctx.send(f"❌ **{name}** 과제를 찾을 수 없습니다.")
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    @tasks.command(name="완료", help="과제 완료")
    async def complete_task(self, ctx, task_type: str, *, name: str):
        """과제 완료 표시"""
        try:
            task_type = "daily" if task_type in {"일일", "daily"} else "weekly"
            task_data = self.load_tasks()
            
            if name in task_data[task_type]:
                task_data[task_type][name]["progress"] = 100
                task_data[task_type][name]["completed"] = True
                self.save_tasks(task_data)
                
                embed = discord.Embed(
                    title="🎉 과제 완료!",
                    description=f"**{name}** - 진행도: 100%",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ **{name}** 과제를 찾을 수 없습니다.")
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    @tasks.command(name="진행도", help="과제 진행도 설정")
    async def set_progress(self, ctx, task_type: str, progress: int, *, name: str):
        """과제 진행도 설정 (0-100)"""
        try:
            if not (0 <= progress <= 100):
                await ctx.send("❌ 진행도는 0~100 사이의 값이어야 합니다.")
                return
            
            task_type = "daily" if task_type in {"일일", "daily"} else "weekly"
            task_data = self.load_tasks()
            
            if name in task_data[task_type]:
                task_data[task_type][name]["progress"] = progress
                if progress == 100:
                    task_data[task_type][name]["completed"] = True
                self.save_tasks(task_data)
                
                # 진행도 바 생성
                progress_bar = self.create_progress_bar(progress)
                
                embed = discord.Embed(
                    title=f"📊 {name}",
                    description=f"{progress_bar}\n진행도: {progress}%",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ **{name}** 과제를 찾을 수 없습니다.")
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    def create_progress_bar(self, progress: int) -> str:
        """진행도 바 생성"""
        filled = progress // 10
        empty = 10 - filled
        return "█" * filled + "░" * empty

    def _format_tasks_text(self, tasks_dict: dict) -> str:
        """과제 텍스트 포맷 (일일/주간 공통)"""
        text = ""
        for name, data in tasks_dict.items():
            progress_bar = self.create_progress_bar(data["progress"])
            status = "✅" if data["completed"] else "⏳"
            text += f"{status} **{name}**: {progress_bar} {data['progress']}%\n"
        return text

    @tasks.command(name="목록", help="과제 목록 표시")
    async def list_tasks(self, ctx, task_type: str = None):
        """과제 목록 표시"""
        try:
            task_data = self.load_tasks()
            embed = discord.Embed(title="📋 과제 목록", color=discord.Color.blue())
            
            # 일일 과제 표시 조건
            show_daily = not task_type or task_type in {"일일", "daily"}
            if show_daily:
                daily_value = self._format_tasks_text(task_data["daily"]) or "등록된 과제가 없습니다."
                embed.add_field(name="📅 일일 과제", value=daily_value, inline=False)
            
            # 주간 과제 표시 조건
            show_weekly = not task_type or task_type in {"주간", "weekly"}
            if show_weekly:
                weekly_value = self._format_tasks_text(task_data["weekly"]) or "등록된 과제가 없습니다."
                embed.add_field(name="📆 주간 과제", value=weekly_value, inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

async def setup(bot):
    try:
        await bot.add_cog(Tasks(bot))
        print("✅ tasks.py 설정 완료")
    except Exception as e:
        print(f"❌ tasks.py 설정 실패: {e}")
        import traceback
        traceback.print_exc()
