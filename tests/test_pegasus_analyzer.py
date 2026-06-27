import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
ANALYZER_PATH = ROOT / "scripts" / "ai_analyzer.py"


def load_analyzer_module():
    spec = importlib.util.spec_from_file_location("ai_analyzer", ANALYZER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Pegasus 返回的（被 ```json 包裹的）应答样例，结构与 SCORING_SYSTEM_PROMPT 约定一致。
FAKE_PEGASUS_REPLY = """```json
{
  "type_classification": "TYPE-A Hook",
  "description": "快速运镜的高能开场",
  "visual_summary": "高饱和色彩，快速剪辑",
  "scores": {
    "aesthetic_beauty": 8,
    "credibility": 7,
    "impact": 9,
    "memorability": 8,
    "fun_interest": 7
  },
  "selection_reasoning": "冲击力强，适合开场",
  "edit_suggestion": "保留前3秒作为Hook"
}
```"""


class PegasusAnalyzerTests(unittest.TestCase):
    def test_pegasus_parses_response_and_uploads_clip(self):
        """No-network unit test: 模拟 TwelveLabs SDK，验证片段上传 + JSON 解析。"""
        module = load_analyzer_module()

        # 伪造一个 ready 的 asset 与 analyze 应答
        fake_asset = mock.Mock(id="asset123", status="ready")
        fake_client = mock.Mock()
        fake_client.assets.create.return_value = fake_asset
        fake_client.assets.retrieve.return_value = fake_asset
        fake_client.analyze.return_value = mock.Mock(data=FAKE_PEGASUS_REPLY)

        with tempfile.TemporaryDirectory() as tmpdir:
            clip = Path(tmpdir) / "scene-001.mp4"
            clip.write_bytes(b"fake mp4 bytes")

            result = module.call_pegasus_video(
                clip_path=clip,
                scene_num=1,
                video_title="测试视频",
                total_scenes=3,
                api_key="dummy-key",
                client=fake_client,
            )

        self.assertIsNotNone(result)
        self.assertEqual(result["type_classification"], "TYPE-A Hook")
        self.assertEqual(result["scores"]["impact"], 9)
        # 上传的是完整片段，而非单帧
        fake_client.assets.create.assert_called_once()
        self.assertEqual(fake_client.assets.create.call_args.kwargs["method"], "direct")
        fake_client.analyze.assert_called_once()

    def test_pegasus_missing_key_returns_none(self):
        """无 API key 时安全返回 None（不抛异常、不改变默认行为）。"""
        module = load_analyzer_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            clip = Path(tmpdir) / "scene-001.mp4"
            clip.write_bytes(b"fake mp4 bytes")
            result = module.call_pegasus_video(clip_path=clip, scene_num=1, api_key="")
        self.assertIsNone(result)

    @unittest.skipUnless(
        os.environ.get("TWELVELABS_API_KEY"),
        "需要 TWELVELABS_API_KEY 进行真实 Pegasus 调用",
    )
    def test_pegasus_live_analyze_returns_text(self):
        """Live test（默认跳过）：真实调用 Pegasus，校验返回的 .data 为文本。

        需要 ffmpeg 生成一个 >=4s、>=360p 的片段。
        """
        import shutil
        import subprocess

        if not shutil.which("ffmpeg"):
            self.skipTest("需要 ffmpeg 生成测试片段")

        module = load_analyzer_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            clip = Path(tmpdir) / "clip.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-f", "lavfi",
                    "-i", "testsrc=duration=6:size=640x360:rate=15",
                    "-pix_fmt", "yuv420p", "-y", str(clip),
                ],
                check=True,
                capture_output=True,
            )
            result = module.call_pegasus_video(
                clip_path=clip,
                scene_num=1,
                api_key=os.environ["TWELVELABS_API_KEY"],
            )
        # 真实模型不保证返回严格 JSON；只断言"调用成功且拿到结构化结果"。
        self.assertIsNotNone(result)
        self.assertIn("scores", result)


if __name__ == "__main__":
    unittest.main()
