using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Data.SqlClient;
using System.Data;


public partial class _Default : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {

    }
    protected void Button1_Click(object sender, EventArgs e)
    {
        string username = this.TextBox1.Text.Trim();
        string pwd = this.TextBox2.Text.Trim();
        SqlConnection conn = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123;");
        conn.Open();
        string strsql = "select * from yonghu where name='" + username + "' and id='" + pwd + "'";
        SqlCommand cmd = new SqlCommand(strsql, conn);
        SqlDataReader dr = cmd.ExecuteReader();
        if (dr.Read())
        {
            Session["name"] = dr["name"];
            Session["id"] = dr["id"];
            if (TextBox1.Text == Session["name"].ToString() && TextBox2.Text == Session["id"].ToString())
            {
                Response.Redirect("~/shouye.aspx");
            }
        }
        else
        {
            Response.Write(@"<script language='javascript'>alert('输入错误');</script>");
        }
    }
}