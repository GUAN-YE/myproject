using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace 第二题
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void button4_Click(object sender, EventArgs e)
        {
            if (textBox1.Text != "")
            {
                if (!listBox1.Items.Contains(textBox1.Text))
                {
                    listBox1.Items.Add(textBox1.Text);
                }
                else
                {
                    MessageBox.Show("输入重复了，亲！");
                }
            }
        }

        private void 移去项目_Click(object sender, EventArgs e)
        {
            listBox1.Items.Remove(listBox1.Text);
        }

        private void button5_Click(object sender, EventArgs e)
        {
            if (listBox1.Items.Count == 0)
            {
                MessageBox.Show("没了");
            }
            else
            {
                listBox1.Items.Clear();
            }               
        }

        private void button2_Click(object sender, EventArgs e)
        {
            listBox2.Items.Remove(listBox2.Text);
        }

        private void button3_Click(object sender, EventArgs e)
        {
            if (textBox1.Text != "")
            {
                if (!listBox2.Items.Contains(textBox1.Text))
                {
                    listBox2.Items.Add(textBox1.Text);
                }
                else
                {
                    MessageBox.Show("输入重复了，亲！");
                }
            }
        }

        private void button6_Click(object sender, EventArgs e)
        {
            if (listBox2.Items.Count == 0)
            {
                MessageBox.Show("没了");
            }
            else
            {
                listBox2.Items.Clear();
            } 
             
        }

        private void listBox1_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (listBox1.SelectedIndex >= 0)
            {
                listBox2.Items.Add(listBox1.SelectedItem);
                listBox1.Items.RemoveAt(listBox1.SelectedIndex);
            }
             
        }

        private void button8_Click(object sender, EventArgs e)
        {
            if (listBox2.SelectedIndex >= 0)
            {
                listBox1.Items.Add(listBox2.SelectedItem);
                listBox2.Items.RemoveAt(listBox2.SelectedIndex);
            }
        }

        private void button7_Click(object sender, EventArgs e)
        { 
            {
                listBox2.Items.Add(listBox1.Items);
                listBox1.Items.Clear();
            }
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }
    }
}
